"""Strategic reasoning for construction/interior bids (LLM + fallback)."""

from .strategic_advisor import StrategicAdvisor, generate_strategy, load_sample_inputs

__all__ = ["StrategicAdvisor", "generate_strategy", "load_sample_inputs"]
