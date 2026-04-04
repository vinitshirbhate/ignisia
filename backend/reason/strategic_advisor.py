from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List
from urllib import error, request

from dotenv import load_dotenv

_THIS_DIR = Path(__file__).resolve().parent
load_dotenv(_THIS_DIR.parent / ".env")
load_dotenv(_THIS_DIR / ".env")

# proposal + external shapes — see main.StrategyRequest docstring

SYSTEM_PROMPT = """You are an expert business strategist for SME construction/interior tenders.

Rules:
* Do NOT recalculate project totals; use figures given in PROJECT DATA only.
* Minimum margin from constraints must be respected; never recommend loss-making bids.
* If competitor price is below the SME's estimated production cost: do NOT advise matching or undercutting; pivot to value-based differentiation.

Return JSON only. Use this exact top-level shape (you may omit "financials" and "scenario_comparison" — the server will fill those):
{
  "strategy": "short label e.g. Value-Based Differentiation",
  "recommended_bid_price": number,
  "win_probability": 0.0-1.0,
  "risk_score": "Low" | "Medium" | "High",
  "decision": { "price_strategy": "...", "reason": "..." },
  "strategic_actions": [ { "action": "...", "impact": "..." } ],
  "positioning": { "type": "...", "message": "..." },
  "explanation": "...",
  "confidence_score": 0.0-1.0
}
"""


def _user_prompt(proposal_json: str, external_block: str) -> str:
    return f"""PROJECT DATA:
{proposal_json}

EXTERNAL FACTORS:
{external_block}

Respond with JSON only."""


def _base_cost(proposal: Dict[str, Any]) -> float:
    if "grand_total" in proposal:
        return float(proposal["grand_total"])
    st = proposal.get("summary_totals") or {}
    base = float(st.get("total_project_cost", 0) or 0)
    cont = proposal.get("contingency") or {}
    amt = float(cont.get("amount", 0) or 0)
    return base + amt if base else 0.0


def _min_margin_pct(external: Dict[str, Any]) -> float:
    c = external.get("constraints") or {}
    return float(c.get("min_margin_percent", 15) or 15) / 100.0


def _competitor_price(external: Dict[str, Any]) -> float:
    ef = external.get("external_factors") or external
    return float(ef.get("competitor_price", 0) or 0)


def _external_factors(external: Dict[str, Any]) -> Dict[str, Any]:
    return external.get("external_factors") or external


def _margin_on_cost_pct(cost: float, bid: float) -> float:
    if cost <= 0:
        return 0.0
    return round((bid - cost) / cost * 100, 2)


def _price_diff_pct(recommended: float, competitor: float) -> float:
    if competitor <= 0:
        return 0.0
    return round((recommended - competitor) / competitor * 100, 1)


def _money(n: float) -> int:
    return int(round(float(n)))


def _scenario_result(margin_percent: float, min_margin_pct: float) -> str:
    """margin_percent is (bid - cost) / cost * 100; min_margin_pct is fraction e.g. 0.15."""
    if margin_percent < 0:
        return "LOSS — rejected"
    if margin_percent + 0.01 < min_margin_pct * 100:
        return "Low margin — high risk"
    return "Optimal strategy"


def _scenario_comparison(
    cost: float,
    competitor: float,
    min_bid: float,
    recommended: float,
    min_margin_pct: float,
) -> Dict[str, Any]:
    aggressive_bid = competitor if competitor > 0 else cost * 0.95
    balanced_bid = round(max(cost * 1.03, min(cost * 1.15, (min_bid + recommended) / 2)))
    if competitor > 0 and competitor < min_bid:
        balanced_bid = int(round(max(cost * 1.025, (competitor + min_bid) / 2)))

    def row(bid: float) -> Dict[str, Any]:
        m = _margin_on_cost_pct(cost, bid)
        return {
            "bid_price": _money(bid),
            "margin": m,
            "result": _scenario_result(m, min_margin_pct),
        }

    value_row = row(recommended)
    if value_row["margin"] + 0.05 >= min_margin_pct * 100:
        value_row["result"] = "Optimal strategy"

    return {
        "aggressive_pricing": row(aggressive_bid),
        "balanced_pricing": row(balanced_bid),
        "value_based": value_row,
    }


def _risk_label(external: Dict[str, Any], competitor_below_cost: bool, margin_pct: float, min_margin_pct: float) -> str:
    ef = _external_factors(external)
    trend = str(ef.get("material_trend", "")).lower()
    market = str(ef.get("market_condition", "")).lower()
    if competitor_below_cost and trend == "increasing":
        return "High"
    if margin_pct < min_margin_pct * 100 - 0.25:
        return "High"
    if competitor_below_cost or market == "competitive":
        return "Medium"
    return "Low"


def _coerce_actions(raw: Any, fallback: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if isinstance(raw, list):
        for item in raw[:8]:
            if isinstance(item, dict) and "action" in item:
                out.append(
                    {
                        "action": str(item.get("action", "")),
                        "impact": str(item.get("impact", "")),
                    }
                )
            elif isinstance(item, str):
                out.append({"action": item, "impact": "Supports differentiation"})
    return out if out else fallback


def _coerce_positioning(raw: Any, fb_type: str, fb_msg: str) -> Dict[str, str]:
    if isinstance(raw, dict):
        return {
            "type": str(raw.get("type", fb_type)),
            "message": str(raw.get("message", fb_msg)),
        }
    if isinstance(raw, str):
        return {"type": fb_type, "message": raw}
    return {"type": fb_type, "message": fb_msg}


def _coerce_decision(raw: Any, price_strategy: str, reason: str) -> Dict[str, str]:
    if isinstance(raw, dict):
        return {
            "price_strategy": str(raw.get("price_strategy", price_strategy)),
            "reason": str(raw.get("reason", reason)),
        }
    return {"price_strategy": price_strategy, "reason": reason}


class StrategicAdvisor:
    """LLM strategist (OpenRouter) + deterministic financials and scenarios."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")

    def _recommended_bid(self, cost: float, comp: float, min_bid: float) -> float:
        if cost > 0 and comp > 0 and comp >= min_bid:
            return round(max(min_bid, comp * 0.98), 2)
        return round(min_bid, 2) if min_bid else 0.0

    def fallback_strategy(self, proposal: Dict[str, Any], external: Dict[str, Any]) -> Dict[str, Any]:
        return self._finalize({}, proposal, external)

    def _finalize(
        self,
        ai: Dict[str, Any],
        proposal: Dict[str, Any],
        external: Dict[str, Any],
    ) -> Dict[str, Any]:
        cost = _base_cost(proposal)
        min_margin_pct = _min_margin_pct(external)
        min_bid = cost * (1.0 + min_margin_pct) if cost > 0 else 0.0
        comp = _competitor_price(external)
        competitor_below = cost > 0 and comp > 0 and comp < cost

        raw_rec = ai.get("recommended_bid_price")
        try:
            rec = float(raw_rec) if raw_rec is not None else self._recommended_bid(cost, comp, min_bid)
        except (TypeError, ValueError):
            rec = self._recommended_bid(cost, comp, min_bid)
        if min_bid > 0:
            rec = max(rec, min_bid)

        margin_pct = _margin_on_cost_pct(cost, rec)
        pct_vs_comp = _price_diff_pct(rec, comp)

        if competitor_below:
            strat_label = "Value-Based Differentiation"
            price_strategy = "Do NOT match competitor pricing"
            pct_below = round((cost - comp) / cost * 100, 1) if cost > 0 else 0.0
            reason = (
                f"Competitor price is about {pct_below}% below loaded production cost; matching is financially unviable."
            )
            pos_type = "Premium Value Provider"
            pos_msg = (
                "Higher upfront cost justified by durability, schedule certainty, warranty, and lower lifecycle cost."
            )
            actions = [
                {"action": "Offer extended warranty / defect liability period", "impact": "+perceived quality & risk transfer"},
                {"action": "Commit to accelerated milestone plan with penalties/bonuses", "impact": "+schedule credibility"},
                {"action": "Upgrade key finishes with documented specs", "impact": "Clear differentiation vs low bids"},
            ]
            win_p = 0.62 + (0.08 if margin_pct >= min_margin_pct * 100 - 1 else 0.0)
        elif cost > 0 and comp > 0 and comp >= min_bid:
            strat_label = "Competitive Value"
            price_strategy = "Compete near market with margin guardrails"
            reason = "Competitor sits at or above your margin-safe floor; you can shade price without breaching minimums."
            pos_type = "Reliable Delivery Partner"
            pos_msg = "Competitive price with transparent BOQ, controlled changes, and on-time delivery focus."
            actions = [
                {"action": "Tighten payment milestones to cash-flow safety", "impact": "Reduces execution risk"},
                {"action": "Offer optional upgrade packages (not core scope)", "impact": "Upside without eroding base bid"},
            ]
            win_p = 0.68
        else:
            strat_label = "Margin-Safe Positioning"
            price_strategy = "Lead on compliance, references, and delivery assurance"
            reason = "Limited competitor signal; anchor to margin-safe bid and strengthen non-price proof points."
            pos_type = "Trusted Regional Contractor"
            pos_msg = "Documented quality, supervision, and handover discipline."
            actions = [
                {"action": "Include reference projects and QA checklist", "impact": "Builds procurement confidence"},
            ]
            win_p = 0.58

        win_p = float(ai.get("win_probability", win_p))
        win_p = max(0.05, min(0.95, win_p))

        risk = str(ai.get("risk_score", _risk_label(external, competitor_below, margin_pct, min_margin_pct)))
        if risk not in {"Low", "Medium", "High"}:
            risk = _risk_label(external, competitor_below, margin_pct, min_margin_pct)

        conf = float(ai.get("confidence_score", 0.72 if competitor_below else 0.65))
        conf = max(0.0, min(1.0, conf))

        strategy = str(ai.get("strategy", strat_label))
        explanation = str(
            ai.get(
                "explanation",
                f"Estimated cost ~{_money(cost):,}; competitor {_money(comp):,} vs recommended {_money(rec):,}. "
                f"Maintain at least {min_margin_pct*100:.0f}% margin on cost unless scope changes.",
            )
        )

        decision = _coerce_decision(ai.get("decision"), price_strategy, reason)
        positioning = _coerce_positioning(ai.get("positioning"), pos_type, pos_msg)
        raw_actions = ai.get("strategic_actions")
        if not raw_actions and isinstance(ai.get("value_additions"), list):
            raw_actions = [
                {"action": str(x), "impact": "Adds perceived value vs lowest bid"}
                for x in ai["value_additions"]
            ]
        strategic_actions = _coerce_actions(raw_actions, actions)

        financials = {
            "estimated_cost": _money(cost),
            "recommended_bid_price": _money(rec),
            "expected_margin_percent": margin_pct,
            "competitor_price": _money(comp) if comp > 0 else 0,
            "price_difference_percent": pct_vs_comp,
        }

        scenarios = _scenario_comparison(cost, comp, min_bid, rec, min_margin_pct)

        return {
            "strategy": strategy,
            "financials": financials,
            "decision": decision,
            "win_probability": round(win_p, 2),
            "risk_score": risk,
            "strategic_actions": strategic_actions,
            "positioning": positioning,
            "scenario_comparison": scenarios,
            "explanation": explanation,
            "confidence_score": round(conf, 3),
        }

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if "```" in cleaned:
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)

    def _normalize(self, data: Dict[str, Any], proposal: Dict[str, Any], external: Dict[str, Any]) -> Dict[str, Any]:
        return self._finalize(data, proposal, external)

    async def generate_strategy(self, proposal: Dict[str, Any], external: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            return self.fallback_strategy(proposal, external)

        proposal_json = json.dumps(proposal, ensure_ascii=True, indent=2)
        external_block = json.dumps(external, ensure_ascii=True, indent=2)
        user_content = _user_prompt(proposal_json, external_block)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.25,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            req = request.Request(
                self.base_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with request.urlopen(req, timeout=45) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            parsed = self._parse_json(content)
            return self._normalize(parsed, proposal, external)
        except (error.URLError, error.HTTPError, KeyError, ValueError, TypeError, json.JSONDecodeError):
            return self.fallback_strategy(proposal, external)


async def generate_strategy(proposal: Dict[str, Any], external: Dict[str, Any]) -> Dict[str, Any]:
    return await StrategicAdvisor().generate_strategy(proposal, external)


def load_sample_inputs() -> tuple[Dict[str, Any], Dict[str, Any]]:
    prop_path = _THIS_DIR / "proposal.json"
    ext_path = _THIS_DIR / "external.json"
    with open(prop_path, encoding="utf-8") as f:
        proposal = json.load(f)
    with open(ext_path, encoding="utf-8") as f:
        external = json.load(f)
    return proposal, external
