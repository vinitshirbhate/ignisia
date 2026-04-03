from __future__ import annotations

from typing import List, Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from pricing_comp.pricing_engine import PricingEngine


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


app = FastAPI(
    title="Pricing Engine API",
    description="Intelligent pricing API for AI-powered RFP bidding.",
    version="1.0.0",
)


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
