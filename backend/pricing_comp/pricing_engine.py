from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any, Dict, List, Literal, Tuple

from pricing_comp.ai_decision_engine import AIDecisionEngine


RiskLevel = Literal["low", "medium", "high"]
DemandLevel = Literal["low", "medium", "high"]
UrgencyLevel = Literal["low", "medium", "high"]
VolatilityLevel = Literal["low", "medium", "high"]
BusinessGoal = Literal["maximize_profit", "win_rate", "balanced"]
ClientImportance = Literal["low", "medium", "high"]


@dataclass
class CompetitorAnalysis:
    average_price: float
    min_price: float
    max_price: float
    spread: float
    intensity: Literal["low", "medium", "high"]
    # 0-1 score where 1.0 means we are significantly cheaper than most competitors
    competitiveness_score: float


class PricingEngine:
    """
    Production-ready pricing engine for AI-powered RFP bidding.

    This engine is intentionally rule-based and modular so that future
    machine-learning models can progressively replace individual components
    (e.g. market adjustment, risk buffer, confidence scoring) without
    changing the public interface.
    """

    def __init__(
        self,
        *,
        material_cost: float,
        labor_cost: float,
        logistics_cost: float,
        overhead_cost: float,
        tax_rate: float,
        competitor_prices: List[float],
        market_demand_level: DemandLevel,
        project_urgency: UrgencyLevel,
        seasonality_factor: float,
        location_multiplier: float,
        min_margin_threshold: float,
        target_margin: float,
        cost_volatility: VolatilityLevel,
        business_goal: BusinessGoal,
        client_importance: ClientImportance,
    ) -> None:
        # Core input parameters
        self.material_cost = float(material_cost)
        self.labor_cost = float(labor_cost)
        self.logistics_cost = float(logistics_cost)
        self.overhead_cost = float(overhead_cost)
        self.tax_rate = float(tax_rate)
        self.competitor_prices = [float(p) for p in competitor_prices if p is not None and p > 0]
        self.market_demand_level = market_demand_level
        self.project_urgency = project_urgency
        self.seasonality_factor = float(seasonality_factor)
        self.location_multiplier = float(location_multiplier)
        self.min_margin_threshold = float(min_margin_threshold)
        self.target_margin = float(target_margin)
        self.cost_volatility = cost_volatility
        self.business_goal = business_goal
        self.client_importance = client_importance

        # Internal trace for explainability
        self._reasoning: List[str] = []

    # ---------------------------------------------------------------------
    # Core computations
    # ---------------------------------------------------------------------

    def calculate_base_cost(self) -> float:
        """
        Compute the fully loaded base cost including multipliers and tax.
        """
        direct_cost = self.material_cost + self.labor_cost + self.logistics_cost
        overhead = self.overhead_cost
        pre_multiplier_cost = direct_cost + overhead

        # Apply location and seasonality as multiplicative factors
        geo_adjusted_cost = pre_multiplier_cost * max(self.location_multiplier, 0.0)
        seasonal_cost = geo_adjusted_cost * max(self.seasonality_factor, 0.0)

        # Apply tax on top of operational cost
        tax_multiplier = 1.0 + max(self.tax_rate, 0.0)
        base_cost = seasonal_cost * tax_multiplier

        self._reasoning.append(
            f"Calculated base cost from direct + overhead costs with location, seasonality, and tax multipliers: {base_cost:.2f}."
        )
        return base_cost

    def calculate_min_safe_price(self, base_cost: float) -> float:
        """
        Compute minimum safe selling price given required margin threshold.
        """
        # Ensure positive margin constraint
        min_margin = max(self.min_margin_threshold, 0.0)
        min_safe_price = base_cost * (1.0 + min_margin)

        self._reasoning.append(
            f"Computed minimum safe price using minimum margin threshold {min_margin:.2%}: {min_safe_price:.2f}."
        )
        return min_safe_price

    def analyze_competitors(self) -> CompetitorAnalysis:
        """
        Analyze competitor prices to derive intensity and competitiveness metrics.
        """
        if not self.competitor_prices:
            # With no competitor data, assume medium intensity but unknown spread.
            self._reasoning.append("No competitor pricing data available; assuming medium competition intensity.")
            return CompetitorAnalysis(
                average_price=0.0,
                min_price=0.0,
                max_price=0.0,
                spread=0.0,
                intensity="medium",
                competitiveness_score=0.0,
            )

        avg = mean(self.competitor_prices)
        mn = min(self.competitor_prices)
        mx = max(self.competitor_prices)
        spread = mx - mn

        # Intensity heuristics based on clustering of competitor prices
        # Smaller spread relative to average implies more intense price competition
        spread_ratio = spread / avg if avg > 0 else 0.0
        if spread_ratio < 0.05:
            intensity: Literal["low", "medium", "high"] = "high"
        elif spread_ratio < 0.15:
            intensity = "medium"
        else:
            intensity = "low"

        # Initial competitiveness score is neutral; adjusted later once we have our price.
        competitiveness_score = 0.5

        self._reasoning.append(
            f"Analyzed {len(self.competitor_prices)} competitor prices "
            f"(avg={avg:.2f}, min={mn:.2f}, max={mx:.2f}, spread_ratio={spread_ratio:.2f}) "
            f"→ competition intensity classified as {intensity}."
        )

        return CompetitorAnalysis(
            average_price=avg,
            min_price=mn,
            max_price=mx,
            spread=spread,
            intensity=intensity,
            competitiveness_score=competitiveness_score,
        )

    def apply_market_adjustments(
        self,
        base_price: float,
        competitor_analysis: CompetitorAnalysis,
    ) -> Tuple[float, float]:
        """
        Apply market and strategic adjustments (demand, urgency, business goal, client importance).

        Returns:
            Tuple of (adjusted_price, total_adjustment_pct).
        """
        price = base_price
        total_adjustment_pct = 0.0

        # Demand adjustment
        demand_factors = {
            "low": -0.03,
            "medium": 0.0,
            "high": 0.05,
        }
        demand_adj = demand_factors.get(self.market_demand_level, 0.0)
        if demand_adj > 0:
            self._reasoning.append(
                f"Increased price due to high market demand ({self.market_demand_level}) by {demand_adj:.1%}."
            )
        elif demand_adj < 0:
            self._reasoning.append(
                f"Reduced price due to weak market demand ({self.market_demand_level}) by {abs(demand_adj):.1%}."
            )
        price *= 1.0 + demand_adj
        total_adjustment_pct += demand_adj

        # Urgency adjustment
        urgency_factors = {
            "low": -0.02,
            "medium": 0.0,
            "high": 0.06,
        }
        urgency_adj = urgency_factors.get(self.project_urgency, 0.0)
        if urgency_adj > 0:
            self._reasoning.append(
                f"Increased price due to high project urgency ({self.project_urgency}) by {urgency_adj:.1%}."
            )
        elif urgency_adj < 0:
            self._reasoning.append(
                f"Slightly reduced price due to low urgency ({self.project_urgency}) by {abs(urgency_adj):.1%}."
            )
        price *= 1.0 + urgency_adj
        total_adjustment_pct += urgency_adj

        # Business goal adjustment
        goal_factors = {
            "maximize_profit": 0.04,
            "win_rate": -0.04,
            "balanced": 0.0,
        }
        goal_adj = goal_factors.get(self.business_goal, 0.0)
        if goal_adj != 0:
            direction = "increased" if goal_adj > 0 else "reduced"
            self._reasoning.append(
                f"{direction.capitalize()} price to reflect business goal '{self.business_goal}' by {abs(goal_adj):.1%}."
            )
        price *= 1.0 + goal_adj
        total_adjustment_pct += goal_adj

        # Client importance adjustment
        client_factors = {
            "low": 0.0,
            "medium": -0.01,
            "high": -0.03,
        }
        client_adj = client_factors.get(self.client_importance, 0.0)
        if client_adj != 0:
            self._reasoning.append(
                f"Adjusted price for client importance '{self.client_importance}' by {client_adj:.1%}."
            )
        price *= 1.0 + client_adj
        total_adjustment_pct += client_adj

        # Competition intensity nudges the price as well
        competition_factors = {
            "low": 0.01,
            "medium": 0.0,
            "high": -0.03,
        }
        competition_adj = competition_factors.get(competitor_analysis.intensity, 0.0)
        if competition_adj != 0:
            if competition_adj < 0:
                self._reasoning.append(
                    "Competition is intense; applying downward adjustment "
                    f"of {abs(competition_adj):.1%} to stay competitive."
                )
            else:
                self._reasoning.append(
                    "Competition spread is wide; allowing slight upward adjustment "
                    f"of {competition_adj:.1%} without risking win rate."
                )
        price *= 1.0 + competition_adj
        total_adjustment_pct += competition_adj

        return price, total_adjustment_pct

    def apply_risk_adjustments(self, base_price: float) -> Tuple[float, RiskLevel, float]:
        """
        Apply risk buffer based on cost volatility and strategic posture.

        Returns:
            Tuple of (adjusted_price, risk_level, risk_buffer_pct).
        """
        price = base_price

        # Baseline risk buffer by volatility
        volatility_buffers = {
            "low": 0.01,
            "medium": 0.03,
            "high": 0.06,
        }
        buffer_pct = volatility_buffers.get(self.cost_volatility, 0.03)

        # Modulate risk buffer by business goal: profit focus accepts more buffer,
        # win-rate focus accepts less buffer to remain attractive.
        if self.business_goal == "maximize_profit":
            buffer_pct *= 1.2
        elif self.business_goal == "win_rate":
            buffer_pct *= 0.7

        # Ensure a sensible cap for stability
        buffer_pct = min(max(buffer_pct, 0.0), 0.12)

        if buffer_pct > 0:
            self._reasoning.append(
                f"Applied risk buffer for cost volatility '{self.cost_volatility}' "
                f"and business goal '{self.business_goal}' of {buffer_pct:.1%}."
            )

        price *= 1.0 + buffer_pct

        # Derive qualitative risk level for reporting
        if buffer_pct <= 0.02:
            risk_level: RiskLevel = "low"
        elif buffer_pct <= 0.06:
            risk_level = "medium"
        else:
            risk_level = "high"

        return price, risk_level, buffer_pct

    # ---------------------------------------------------------------------
    # Scoring and scenario utilities
    # ---------------------------------------------------------------------

    @staticmethod
    def score_competitiveness(
        our_price: float,
        competitor_avg: float,
        competitor_spread: float,
    ) -> float:
        """
        Estimate how competitive our price is relative to the market.

        Returns a score in [0, 1]:
            - ~0.5: roughly aligned with market
            - >0.5: cheaper than market (more competitive)
            - <0.5: more expensive (less competitive)
        """
        del competitor_spread  # kept for backward-compatible signature
        if our_price <= 0 or competitor_avg <= 0:
            return 1.0
        # Required formula: competitiveness_score = competitor_avg / recommended_price
        return max(0.0, float(competitor_avg / our_price))

    def simulate_scenarios(self, margin_offsets: List[float]) -> List[Dict[str, float]]:
        """
        Simulate alternative pricing scenarios by shifting target margin.

        Args:
            margin_offsets: list of additive margin offsets (e.g. [-0.05, 0.0, 0.05])

        Returns:
            List of dictionaries with scenario_price and competitiveness_score.
        """
        base_cost = self.calculate_base_cost()
        competitor_analysis = self.analyze_competitors()
        scenarios = []

        for offset in margin_offsets:
            # For each scenario, we temporarily adjust target margin but keep
            # minimum margin safeguards via min_safe_price in compute_final_price.
            original_target = self.target_margin
            self.target_margin = max(0.0, original_target + offset)

            price_dict = self.compute_final_price(reuse_base_cost=base_cost, reuse_competitors=competitor_analysis)
            scenarios.append(
                {
                    "margin_offset": float(offset),
                    "recommended_price": float(price_dict["recommended_price"]),
                    "competitiveness_score": float(price_dict["competitiveness_score"]),
                }
            )

            # Restore original target for subsequent iterations.
            self.target_margin = original_target

        return scenarios

    # ---------------------------------------------------------------------
    # Final price computation
    # ---------------------------------------------------------------------

    def _compute_confidence_score(
        self,
        competitiveness_score: float,
        risk_level: RiskLevel,
        has_competitor_data: bool,
    ) -> float:
        """
        Derive an overall confidence score in the recommendation.

        Combines:
            - availability of competitor data
            - pricing competitiveness
            - risk posture
        """
        score = 0.5

        # Competitor data gives stronger signal about where we sit in the market.
        if has_competitor_data:
            score += 0.15
        else:
            score -= 0.05

        # Being extremely off-market (too high or too low) should reduce confidence.
        proximity_to_neutral = 1.0 - abs(competitiveness_score - 0.5) * 2.0
        score += 0.2 * max(0.0, proximity_to_neutral)

        # Higher risk should slightly reduce confidence.
        risk_penalty = {"low": 0.0, "medium": 0.07, "high": 0.12}.get(risk_level, 0.07)
        score -= risk_penalty

        return max(0.0, min(1.0, score))

    def _build_ai_context(self, price_result: Dict[str, object]) -> Dict[str, Any]:
        return {
            "base_cost": float(price_result["base_cost"]),
            "min_safe_price": float(price_result["min_safe_price"]),
            "recommended_price": float(price_result["recommended_price"]),
            "competitor_avg": float(price_result["competitor_avg"]),
            "competitor_prices": [float(x) for x in self.competitor_prices],
            "risk_level": str(price_result["risk_level"]),
            "market_demand_level": self.market_demand_level,
            "project_urgency": self.project_urgency,
            "business_goal": self.business_goal,
            "client_importance": self.client_importance,
        }

    async def generate_ai_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ai_engine = AIDecisionEngine()
        return await ai_engine.generate_ai_decision(context)

    def compute_final_price(
        self,
        *,
        reuse_base_cost: float | None = None,
        reuse_competitors: CompetitorAnalysis | None = None,
    ) -> Dict[str, object]:
        """
        Compute the final recommended price and metadata.

        The method respects:
            - never price below base cost
            - maintain minimum safe margin
            - avoid undercutting when competitors are below safe price
        """
        # Reset reasoning trace for each top-level call.
        self._reasoning = []

        base_cost = reuse_base_cost if reuse_base_cost is not None else self.calculate_base_cost()
        min_safe_price = self.calculate_min_safe_price(base_cost)
        competitor_analysis = reuse_competitors if reuse_competitors is not None else self.analyze_competitors()

        # Start from a target margin on top of base cost, but never below min_safe_price.
        target_price = base_cost * (1.0 + max(self.target_margin, self.min_margin_threshold))
        target_price = max(target_price, min_safe_price)
        self._reasoning.append(
            f"Initial target price based on target margin {self.target_margin:.2%} "
            f"and minimum safe price: {target_price:.2f}."
        )

        # Apply market adjustments first (demand, urgency, competition, strategic posture).
        market_adjusted_price, market_adj_pct = self.apply_market_adjustments(target_price, competitor_analysis)

        # Respect the rule: If competitor average is below min_safe_price, do not undercut min_safe_price.
        if competitor_analysis.average_price > 0 and competitor_analysis.average_price < min_safe_price:
            self._reasoning.append(
                "Average competitor price is below minimum safe price; "
                "refusing to undercut and enforcing safe margin floor."
            )
            market_adjusted_price = max(market_adjusted_price, min_safe_price)

        # Apply risk buffer on top of market-adjusted price.
        risk_adjusted_price, risk_level, risk_buffer_pct = self.apply_risk_adjustments(market_adjusted_price)

        # Enforce hard constraints:
        #   - Never below base cost.
        #   - Maintain minimum safe price.
        constrained_price = max(risk_adjusted_price, base_cost, min_safe_price)
        if constrained_price > risk_adjusted_price:
            self._reasoning.append(
                "Final price was raised to meet base cost and minimum safe price constraints."
            )

        # Compute a soft pricing band around the recommendation.
        # Band width reflects overall adjustments and risk buffer to encode uncertainty.
        base_band_width = 0.05  # 5% baseline band
        dynamic_band = abs(market_adj_pct) + abs(risk_buffer_pct)
        total_band_pct = min(0.15, base_band_width + dynamic_band)
        band_low = constrained_price * (1.0 - total_band_pct / 2)
        band_high = constrained_price * (1.0 + total_band_pct / 2)

        # Competitiveness scoring relative to competitor landscape
        competitiveness_score = self.score_competitiveness(
            constrained_price,
            competitor_analysis.average_price,
            competitor_analysis.spread,
        )

        confidence_score = self._compute_confidence_score(
            competitiveness_score,
            risk_level,
            has_competitor_data=bool(self.competitor_prices),
        )

        # Log final reasoning summary.
        self._reasoning.append(
            f"Final recommended price: {constrained_price:.2f} "
            f"(band {band_low:.2f} – {band_high:.2f}), "
            f"competitiveness score {competitiveness_score:.2f}, "
            f"overall confidence {confidence_score:.2f}."
        )

        result = {
            "base_cost": float(round(base_cost, 2)),
            "min_safe_price": float(round(min_safe_price, 2)),
            "recommended_price": float(round(constrained_price, 2)),
            "pricing_band": {
                "low": float(round(band_low, 2)),
                "high": float(round(band_high, 2)),
            },
            "competitor_avg": float(round(competitor_analysis.average_price, 2)),
            "competitiveness_score": float(round(competitiveness_score, 3)),
            "risk_level": risk_level,
            "confidence_score": float(round(confidence_score, 3)),
            "reasoning": self._reasoning,
        }
        # Keep sync pipeline deterministic with robust fallback AI output.
        fallback_ai = AIDecisionEngine().fallback_decision(self._build_ai_context(result))
        result["ai_decision"] = fallback_ai
        return result

    async def compute_final_price_with_ai(self) -> Dict[str, object]:
        result = self.compute_final_price()
        result["ai_decision"] = await self.generate_ai_decision(self._build_ai_context(result))
        return result

    async def simulate_scenarios_with_ai(self, margin_offsets: List[float]) -> List[Dict[str, object]]:
        scenarios: List[Dict[str, object]] = []
        for item in self.simulate_scenarios(margin_offsets):
            context = {
                "base_cost": self.calculate_base_cost(),
                "min_safe_price": self.calculate_min_safe_price(self.calculate_base_cost()),
                "recommended_price": item["recommended_price"],
                "competitor_avg": mean(self.competitor_prices) if self.competitor_prices else 0.0,
                "competitor_prices": self.competitor_prices,
                "risk_level": self.cost_volatility,
                "market_demand_level": self.market_demand_level,
                "project_urgency": self.project_urgency,
                "business_goal": self.business_goal,
                "client_importance": self.client_importance,
            }
            ai_decision = await self.generate_ai_decision(context)
            scenarios.append(
                {
                    "margin_offset": item["margin_offset"],
                    "recommended_price": item["recommended_price"],
                    "competitiveness_score": item["competitiveness_score"],
                    "win_probability": ai_decision["win_probability"],
                    "ai_decision": ai_decision,
                }
            )
        return scenarios


__all__ = ["PricingEngine", "CompetitorAnalysis"]

