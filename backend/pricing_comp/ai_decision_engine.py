from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Literal
from urllib import error, request

from dotenv import load_dotenv


# Load env from both backend root and this package directory if present.
_THIS_DIR = Path(__file__).resolve().parent
load_dotenv(_THIS_DIR.parent / ".env")
load_dotenv(_THIS_DIR / ".env")


Decision = Literal["COMPETE", "DIFFERENTIATE", "AVOID"]

SYSTEM_PROMPT = (
    "You are an expert sales strategist for SMEs responding to competitive tenders.\n"
    "Your job is to analyze pricing, competition, and risk, and advise whether the SME should compete, "
    "differentiate, or avoid the bid.\n\n"
    "Rules:\n\n"
    "* If price is much higher than competitors -> suggest differentiation or avoidance\n"
    "* If below competitors -> suggest competitive pricing\n"
    "* If risk is high -> warn clearly\n"
    "* Always give actionable business advice\n"
    "* Be realistic and strategic, not optimistic"
)


class AIDecisionEngine:
    """Small AI layer with a safe rule-based fallback."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")

    def fallback_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        competitor_avg = float(context.get("competitor_avg", 0.0) or 0.0)
        recommended = float(context.get("recommended_price", 0.0) or 0.0)
        risk_level = str(context.get("risk_level", "medium"))

        competitiveness = competitor_avg / recommended if recommended > 0 and competitor_avg > 0 else 1.0
        win_probability = 0.55
        win_probability += 0.15 if competitiveness > 1.05 else -0.12 if competitiveness < 0.9 else 0.0
        win_probability += -0.12 if risk_level == "high" else -0.05 if risk_level == "medium" else 0.03
        win_probability = max(0.05, min(0.95, win_probability))

        if risk_level == "high" and competitiveness < 0.9:
            decision: Decision = "AVOID"
        elif competitiveness < 0.95:
            decision = "DIFFERENTIATE"
        else:
            decision = "COMPETE"

        strategy = (
            "Lead with strong value narrative and measurable outcomes."
            if decision == "DIFFERENTIATE"
            else "Compete on pricing with clear delivery confidence."
            if decision == "COMPETE"
            else "Avoid low-probability bid and preserve margin capacity."
        )
        actions = [
            "Align proposal with client-specific outcomes and KPIs.",
            "Document risk mitigations and delivery plan.",
            "Prepare negotiation floor at or above minimum safe price.",
        ]
        loss_reasons = []
        if competitiveness < 0.95:
            loss_reasons.append("Price is above prevailing competitor levels.")
        if risk_level == "high":
            loss_reasons.append("High cost volatility can weaken execution confidence.")

        return {
            "win_probability": round(float(win_probability), 3),
            "decision": decision,
            "strategy": strategy,
            "actions": actions,
            "loss_reasons": loss_reasons,
        }

    async def generate_ai_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate decision via OpenRouter; fallback if key/API/parsing fails."""
        if not self.api_key:
            return self.fallback_decision(context)

        user_prompt = (
            "Analyze this bid context and return JSON only.\n\n"
            f"Context:\n{json.dumps(context, ensure_ascii=True)}\n\n"
            "Return JSON with:\n"
            '{\n"win_probability": float,\n"decision": "...",\n"strategy": "...",\n"actions": [],\n"loss_reasons": []\n}'
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
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
            with request.urlopen(req, timeout=20) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            parsed = self._coerce_json(content)
            return self._normalize_decision(parsed)
        except (error.URLError, error.HTTPError, KeyError, ValueError, TypeError, json.JSONDecodeError):
            return self.fallback_decision(context)

    @staticmethod
    def _coerce_json(text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if "```" in cleaned:
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)

    def _normalize_decision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        fallback = self.fallback_decision(data)
        decision = str(data.get("decision", fallback["decision"])).upper()
        if decision not in {"COMPETE", "DIFFERENTIATE", "AVOID"}:
            decision = fallback["decision"]
        return {
            "win_probability": round(float(max(0.0, min(1.0, float(data.get("win_probability", fallback["win_probability"]))))), 3),
            "decision": decision,
            "strategy": str(data.get("strategy", fallback["strategy"])),
            "actions": [str(x) for x in data.get("actions", fallback["actions"])][:6],
            "loss_reasons": [str(x) for x in data.get("loss_reasons", fallback["loss_reasons"])][:6],
        }

