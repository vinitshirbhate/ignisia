"""Map RFP analyze payload + strategy JSON into ProposalRequest for PDF generation."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from schemas import (
    ClientInfo,
    CommercialTerms,
    CompanyInfo,
    DocumentMeta,
    PricingItem,
    ProposalRequest,
)


def _get_cost_block(ai_proposal: dict[str, Any]) -> dict[str, Any] | None:
    pr = ai_proposal.get("pricing_result")
    if not isinstance(pr, dict) or pr.get("error"):
        return None
    if isinstance(pr.get("proposal"), dict):
        return pr["proposal"]  # type: ignore[return-value]
    if isinstance(pr.get("project_summary"), dict):
        return {k: v for k, v in pr.items() if k not in ("external", "error", "raw_response")}
    return None


def _money(v: Any) -> str:
    if v is None:
        return "—"
    try:
        n = float(v)
        return f"₹{n:,.0f}"
    except (TypeError, ValueError):
        return str(v)


def _slug_filename(name: str) -> str:
    s = re.sub(r"[^\w\s\-]", "", name, flags=re.UNICODE)
    s = re.sub(r"\s+", "-", s.strip())[:60] or "rfp-response"
    return f"{s}.pdf"


def build_proposal_request_from_rfp_ai(
    ai_proposal: dict[str, Any],
    ai_reason: dict[str, Any],
) -> ProposalRequest:
    raw_analysis = ai_proposal.get("analysis")
    analysis = raw_analysis if isinstance(raw_analysis, dict) else {}
    rfp_name = str(analysis.get("rfp_name") or "RFP Response")

    cost = _get_cost_block(ai_proposal) or {}
    ps = cost.get("project_summary") if isinstance(cost.get("project_summary"), dict) else {}
    materials_block = cost.get("material_costs") if isinstance(cost.get("material_costs"), dict) else {}
    raw_items = materials_block.get("items") if isinstance(materials_block.get("items"), list) else []

    pricing_items: list[PricingItem] = []
    for row in raw_items:
        if not isinstance(row, dict):
            continue
        name = str(row.get("item") or row.get("name") or "Item")
        qty_raw = row.get("quantity")
        try:
            qty_f = float(qty_raw) if qty_raw is not None else 0.0
        except (TypeError, ValueError):
            qty_f = 0.0
        q = max(1, int(round(qty_f))) if qty_f else 1
        try:
            unit = float(row.get("unit_price_ex_gst") or 0)
        except (TypeError, ValueError):
            unit = 0.0
        if unit <= 0 and qty_f:
            try:
                ttl = float(row.get("total_incl_gst") or 0)
            except (TypeError, ValueError):
                ttl = 0.0
            unit = ttl / qty_f if qty_f else 0.0
        pricing_items.append(PricingItem(item=name[:200], quantity=q, unit_cost=max(0.0, unit)))

    labor = cost.get("labor_costs") if isinstance(cost.get("labor_costs"), dict) else {}
    try:
        labor_total = float(labor.get("total_labor_cost") or 0)
    except (TypeError, ValueError):
        labor_total = 0.0
    if labor_total > 0:
        pricing_items.append(PricingItem(item="Labour (estimated)", quantity=1, unit_cost=max(0.0, labor_total)))

    if not pricing_items:
        pricing_items = [PricingItem(item="See executive summary for commercial posture", quantity=1, unit_cost=0)]

    fin = ai_reason.get("financials") if isinstance(ai_reason.get("financials"), dict) else {}
    expl = str(ai_reason.get("explanation") or "").strip()
    fin_line = (
        f"Recommended bid: {_money(fin.get('recommended_bid_price'))}; estimated cost {_money(fin.get('estimated_cost'))}; "
        f"target margin {fin.get('expected_margin_percent', '—')}%; competitor ref. {_money(fin.get('competitor_price'))}."
    )
    executive_summary = "\n\n".join(p for p in (expl, fin_line) if p).strip() or "Strategic RFP response summary."

    raw_actions = ai_reason.get("strategic_actions")
    actions: list[Any] = raw_actions if isinstance(raw_actions, list) else []
    biz_obj: list[str] = []
    for a in actions[:10]:
        if isinstance(a, dict):
            act = str(a.get("action") or "").strip()
            imp = str(a.get("impact") or "").strip()
            biz_obj.append(f"{act} — {imp}".strip(" —"))
        else:
            biz_obj.append(str(a))
    if not biz_obj:
        biz_obj = ["Deliver full RFP scope with margin-safe commercial positioning."]

    decision = ai_reason.get("decision") if isinstance(ai_reason.get("decision"), dict) else {}
    strat = str(ai_reason.get("strategy") or "").strip()
    dec_line = f"{decision.get('price_strategy', '')}: {decision.get('reason', '')}".strip(": ").strip()
    proposed: list[str] = []
    if strat:
        proposed.append(strat)
    if dec_line:
        proposed.append(dec_line)
    try:
        wp = float(ai_reason.get("win_probability"))
        proposed.append(f"Win probability (model): {round(wp * 100)}%.")
    except (TypeError, ValueError):
        pass
    if not proposed:
        proposed = ["Value-aligned response per AI strategy review."]

    scope: list[str] = []
    for row in raw_items:
        if isinstance(row, dict):
            nm = str(row.get("item") or row.get("name") or "").strip()
            if nm:
                scope.append(nm)
    scope = scope[:30]
    if not scope:
        scope = [f"Works as described in RFP: {rfp_name[:120]}"]

    weeks = ps.get("duration_weeks")
    dur = f"Planned duration: {weeks} weeks" if weeks is not None and str(weeks).strip() != "" else ""
    timeline: list[str] = [x for x in (dur,) if x]
    region = str(ps.get("region") or "—")
    state = str(ps.get("state") or "")
    loc = f"{region}, {state}".strip(", ")
    if loc and loc != "—":
        timeline.append(f"Location context: {loc}.")

    deliverables = [str(a.get("action", "")) for a in actions if isinstance(a, dict) and a.get("action")][:12]
    if not deliverables:
        deliverables = ["Priced BOQ narrative", "Strategic positioning aligned to RFP"]

    pos = ai_reason.get("positioning") if isinstance(ai_reason.get("positioning"), dict) else {}
    value_heading = str(pos.get("type") or "Strategic positioning")
    value_points: list[str] = []
    msg = str(pos.get("message") or "").strip()
    if msg:
        value_points.append(msg)
    sc = ai_reason.get("scenario_comparison") if isinstance(ai_reason.get("scenario_comparison"), dict) else {}
    for key, label in (
        ("aggressive_pricing", "Aggressive"),
        ("balanced_pricing", "Balanced"),
        ("value_based", "Value-based"),
    ):
        b = sc.get(key)
        if isinstance(b, dict):
            value_points.append(
                f"{label}: bid {_money(b.get('bid_price'))}, margin {b.get('margin', '—')}%. {b.get('result', '')}".strip()
            )
    value_points = [p for p in value_points if p][:12]

    try:
        sub_ex = float(materials_block.get("subtotal_ex_gst") or 0)
        total_gst = float(materials_block.get("total_gst") or 0)
    except (TypeError, ValueError):
        sub_ex, total_gst = 0.0, 0.0
    gst_pct = (total_gst / sub_ex * 100) if sub_ex > 0 else 18.0

    today = date.today().strftime("%d %b %Y")
    ref = f"IG-RFP-{date.today().strftime('%Y%m%d')}"

    terms: list[str] = [
        "Figures derive from AI-assisted BOQ and strategy; final numbers subject to site validation and RFP clarifications.",
    ]
    rs = ai_reason.get("risk_score")
    if rs:
        terms.append(f"Risk outlook: {rs}.")
    conf = ai_reason.get("confidence_score")
    if conf is not None:
        try:
            terms.append(f"Model confidence score: {float(conf):.2f}.")
        except (TypeError, ValueError):
            terms.append(f"Model confidence score: {conf}.")

    return ProposalRequest(
        company=CompanyInfo(
            name="Ignisia Digital Labs",
            logo_text="IG",
            tag_line="RFP Flow — AI-assisted bidding & construction estimates",
            email="hello@ignisia.com",
            phone="+91 98765 43210",
            address="Pune, Maharashtra, India",
            website="www.ignisia.com",
        ),
        document=DocumentMeta(
            title="RFP Response & Commercial Summary",
            file_name=_slug_filename(rfp_name),
            reference=ref,
            issue_date=today,
            validity="30 days from issue date",
            prepared_by="RFP Flow — AI Proposal & Strategy",
        ),
        client=ClientInfo(
            company_name=rfp_name[:120] or "Client",
            contact_person="Procurement",
            designation="—",
            email="procurement@client.example",
        ),
        project_title=rfp_name[:200],
        executive_summary=executive_summary[:4000],
        business_objectives=biz_obj[:12],
        proposed_solution=proposed[:10],
        scope_of_work=scope,
        timeline=timeline[:10] or ["Milestones per RFP schedule."],
        deliverables=deliverables[:15],
        value_add_heading=value_heading[:120],
        value_add_points=value_points or ["Differentiated delivery and transparent commercial framing."],
        pricing=pricing_items[:40],
        commercial_terms=CommercialTerms(
            gst_percent=round(min(max(gst_pct, 0.0), 28.0), 2),
            payment_terms=[
                "Milestone-based billing aligned to RFP / contract schedule.",
                "GST as per applicable regulations.",
            ],
            terms_and_conditions=terms[:8],
        ),
        authorized_signatory="Authorized Representative",
    )
