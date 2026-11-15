import logging
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)

COST_PER_CALL = {
    "openai_gpt4o": 0.015,
    "openai_gpt4o_mini": 0.003,
    "gemini_flash": 0.003,
    "claude_sonnet": 0.015,
    "grok_vision": 0.01,
    "replicate_flux": 0.25,
    "replicate_sam": 0.10,
    "dalle": 0.08,
    "openai_embedding": 0.0001,
    "openai_chat": 0.005,
}

_daily_costs: dict[str, float] = {}

def track_ai_cost(provider: str, feature: str, user_id: Optional[str] = None):
    cost = COST_PER_CALL.get(provider, 0.01)
    today = date.today().isoformat()
    _daily_costs[today] = _daily_costs.get(today, 0) + cost
    logger.info(f"AI_COST | provider={provider} | feature={feature} | cost=${cost:.4f} | user={user_id or 'unknown'} | daily_total=${_daily_costs[today]:.4f}")

def get_daily_cost(day: Optional[str] = None) -> float:
    day = day or date.today().isoformat()
    return _daily_costs.get(day, 0)

def get_cost_summary() -> dict:
    return {
        "today": get_daily_cost(),
        "costs_by_day": dict(_daily_costs),
    }
