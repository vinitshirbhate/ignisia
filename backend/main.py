from __future__ import annotations

import json
from pathlib import Path
from typing import List, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from pricing_comp.pricing_engine import PricingEngine
from reason.strategic_advisor import StrategicAdvisor, load_sample_inputs


DemandLevel = Literal["low", "medium", "high"]
UrgencyLevel = Literal["low", "medium", "high"]
VolatilityLevel = Literal["low", "medium", "high"]
BusinessGoal = Literal["maximize_profit", "win_rate", "balanced"]
ClientImportance = Literal["low", "medium", "high"]


class PricingRequest(BaseModel):
    material_cost: float = Field(..., ge=0)
    labor_cost: float = Field(..., ge=0)
    logistics_cost: float = Field(..., ge=0)
    overhead_cost: float = Field(..., ge=0)
    tax_rate: float = Field(..., ge=0)
    competitor_prices: List[float] = Field(default_factory=list)
    market_demand_level: DemandLevel
    project_urgency: UrgencyLevel
    seasonality_factor: float = Field(..., gt=0)
    location_multiplier: float = Field(..., gt=0)
    min_margin_threshold: float = Field(..., ge=0)
    target_margin: float = Field(..., ge=0)
    cost_volatility: VolatilityLevel
    business_goal: BusinessGoal
    client_importance: ClientImportance


class ScenarioRequest(PricingRequest):
    margin_offsets: List[float] = Field(default_factory=lambda: [-0.05, 0.0, 0.05])


_BACKEND_ROOT = Path(__file__).resolve().parent


def _strategy_request_openapi_example() -> dict:
    """Same shape as POST body: proposal breakdown + external_factors/constraints."""
    with open(_BACKEND_ROOT / "reason" / "proposal.json", encoding="utf-8") as f:
        proposal = json.load(f)
    with open(_BACKEND_ROOT / "reason" / "external.json", encoding="utf-8") as f:
        external = json.load(f)
    return {"proposal": proposal, "external": external}


class StrategyRequest(BaseModel):
    """
    Client sends two JSON objects:

    * ``proposal`` — cost breakdown (materials, labor, summary_totals, contingency, grand_total).
    * ``external`` — ``external_factors`` (e.g. competitor_price) and ``constraints`` (e.g. min_margin_percent).
    """

    model_config = ConfigDict(json_schema_extra={"examples": [_strategy_request_openapi_example()]})

    proposal: dict = Field(
        ...,
        description="Project cost JSON: project_summary, material_costs, labor_costs, summary_totals, contingency, grand_total.",
    )
    external: dict = Field(
        ...,
        description="Market JSON: external_factors (competitor_price, market_condition, …), constraints (min_margin_percent).",
    )


app = FastAPI(
    title="Pricing Engine API",
    description="Intelligent pricing API for AI-powered RFP bidding.",
    version="1.0.0",
)

# Last successful POST /reason/strategy (so Swagger/Postman/UI can share one result).
_latest_strategy: dict | None = None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _build_engine(payload: PricingRequest) -> PricingEngine:
    return PricingEngine(
        material_cost=payload.material_cost,
        labor_cost=payload.labor_cost,
        logistics_cost=payload.logistics_cost,
        overhead_cost=payload.overhead_cost,
        tax_rate=payload.tax_rate,
        competitor_prices=payload.competitor_prices,
        market_demand_level=payload.market_demand_level,
        project_urgency=payload.project_urgency,
        seasonality_factor=payload.seasonality_factor,
        location_multiplier=payload.location_multiplier,
        min_margin_threshold=payload.min_margin_threshold,
        target_margin=payload.target_margin,
        cost_volatility=payload.cost_volatility,
        business_goal=payload.business_goal,
        client_importance=payload.client_importance,
    )


@app.post("/pricing/recommend")
async def recommend_price(payload: PricingRequest) -> dict:
    engine = _build_engine(payload)
    return await engine.compute_final_price_with_ai()


@app.post("/reason/strategy")
async def reason_strategy(payload: StrategyRequest) -> dict:
    """
    Strategic bid advice. Body must be ``{ "proposal": <cost JSON>, "external": <market JSON> }``
    (same structures as ``reason/proposal.json`` and ``reason/external.json``).
    """
    global _latest_strategy
    advisor = StrategicAdvisor()
    result = await advisor.generate_strategy(payload.proposal, payload.external)
    _latest_strategy = result
    return result


@app.get("/reason/strategy/latest")
async def reason_strategy_latest() -> dict:
    """Return the result of the most recent successful POST /reason/strategy (e.g. for the UI after Swagger)."""
    if _latest_strategy is None:
        raise HTTPException(
            status_code=404,
            detail="No strategy computed yet. Call POST /reason/strategy first, then refresh the UI.",
        )
    return _latest_strategy


@app.get("/reason/strategy/sample")
async def reason_strategy_sample() -> dict:
    proposal, external = load_sample_inputs()
    advisor = StrategicAdvisor()
    return await advisor.generate_strategy(proposal, external)


@app.post("/pricing/simulate")
async def simulate_pricing(payload: ScenarioRequest) -> dict:
    engine = _build_engine(payload)
    baseline = await engine.compute_final_price_with_ai()
    scenarios = await engine.simulate_scenarios_with_ai(payload.margin_offsets)

    return {
        "baseline": baseline,
        "scenarios": scenarios,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
