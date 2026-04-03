"""
MCP Server 2: Labor Costs
Fetches current labor rates by trade and state in India.
Includes statutory costs (PF, ESI) and contractor overhead.
"""

import asyncio
import logging
from datetime import datetime
from fastmcp import FastMCP
import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("labor_costs")

mcp = FastMCP("Labor Costs Server")

# ── State-wise daily wage baselines (INR/day) — Schedule of Rates 2024 ────────
LABOR_RATES = {
    "mason": {
        "maharashtra": 780,  "karnataka": 720,  "delhi": 830,
        "gujarat": 700,      "tamil_nadu": 660,  "telangana": 680,
        "kerala": 850,       "rajasthan": 600,   "up": 580,
        "mp": 560,           "wb": 620,          "punjab": 720,
        "haryana": 760,      "andhra_pradesh": 660, "default": 700,
    },
    "carpenter": {
        "maharashtra": 880,  "karnataka": 820,  "delhi": 930,
        "gujarat": 750,      "tamil_nadu": 720,  "telangana": 750,
        "kerala": 950,       "rajasthan": 650,   "up": 640,
        "default": 800,
    },
    "electrician": {
        "maharashtra": 920,  "karnataka": 870,  "delhi": 970,
        "gujarat": 800,      "tamil_nadu": 780,  "telangana": 800,
        "kerala": 980,       "default": 850,
    },
    "plumber": {
        "maharashtra": 870,  "karnataka": 820,  "delhi": 920,
        "gujarat": 760,      "tamil_nadu": 740,  "default": 820,
    },
    "painter": {
        "maharashtra": 720,  "karnataka": 680,  "delhi": 760,
        "gujarat": 640,      "tamil_nadu": 620,  "default": 680,
    },
    "tile_layer": {
        "maharashtra": 780,  "karnataka": 730,  "delhi": 820,
        "gujarat": 700,      "default": 750,
    },
    "welder": {
        "maharashtra": 900,  "karnataka": 850,  "delhi": 950,
        "default": 860,
    },
    "fabricator": {
        "maharashtra": 850,  "karnataka": 800,  "delhi": 900,
        "default": 820,
    },
    "pool_specialist": {
        "maharashtra": 1200, "karnataka": 1100, "delhi": 1300,
        "gujarat": 1000,     "default": 1100,
    },
    "waterproofing_specialist": {
        "maharashtra": 1100, "karnataka": 1000, "delhi": 1200,
        "default": 1050,
    },
    "supervisor": {
        "maharashtra": 1400, "karnataka": 1250, "delhi": 1500,
        "gujarat": 1200,     "default": 1300,
    },
    "project_manager": {
        "maharashtra": 3000, "karnataka": 2800, "delhi": 3200,
        "default": 2800,
    },
    "unskilled": {
        "maharashtra": 480,  "karnataka": 440,  "delhi": 520,
        "gujarat": 420,      "tamil_nadu": 400,  "telangana": 420,
        "kerala": 550,       "rajasthan": 380,   "up": 370,
        "default": 440,
    },
    "helper": {
        "maharashtra": 450,  "karnataka": 410,  "delhi": 490,
        "default": 430,
    },
}

# Trade composition by project type (workers per 1000 sqft, per week)
TRADE_MIX = {
    "interior_fit_out": {
        "carpenter": 3, "painter": 2, "electrician": 1,
        "plumber": 0.5, "tile_layer": 2, "unskilled": 4,
        "supervisor": 0.5,
    },
    "pool_construction": {
        "mason": 5, "pool_specialist": 2, "electrician": 1,
        "plumber": 2, "waterproofing_specialist": 1,
        "unskilled": 6, "supervisor": 1,
    },
    "bathhouse_renovation": {
        "mason": 2, "carpenter": 1, "electrician": 1,
        "plumber": 1, "tile_layer": 2, "painter": 1,
        "unskilled": 3, "supervisor": 0.5,
    },
    "residential_construction": {
        "mason": 4, "carpenter": 2, "electrician": 1,
        "plumber": 1, "painter": 1, "unskilled": 5,
        "supervisor": 1,
    },
    "commercial_fit_out": {
        "carpenter": 3, "electrician": 2, "plumber": 1,
        "tile_layer": 1, "painter": 1, "welder": 1,
        "unskilled": 3, "supervisor": 1,
    },
    "pool_and_bathhouse": {
        "mason": 4, "pool_specialist": 2, "electrician": 1,
        "plumber": 2, "waterproofing_specialist": 1,
        "tile_layer": 2, "painter": 1, "carpenter": 1,
        "unskilled": 6, "supervisor": 1,
    },
}

# Statutory add-ons
STATUTORY = {
    "pf_rate": 0.12,       # Employer PF contribution
    "esi_rate": 0.0325,    # Employer ESI contribution
    "lwf_monthly": 25,     # Labour Welfare Fund (nominal)
    "bonus_rate": 0.0833,  # Statutory bonus (8.33% of wages)
}

CONTRACTOR_OVERHEAD = 0.18  # 18% overhead + profit for labor contractor


def normalize_state(state: str) -> str:
    """Normalize state name to key format."""
    mapping = {
        "maharashtra": "maharashtra", "mh": "maharashtra",
        "karnataka": "karnataka", "ka": "karnataka",
        "delhi": "delhi", "ncr": "delhi", "new delhi": "delhi",
        "gujarat": "gujarat", "gj": "gujarat",
        "tamil nadu": "tamil_nadu", "tamilnadu": "tamil_nadu", "tn": "tamil_nadu",
        "telangana": "telangana", "ts": "telangana",
        "kerala": "kerala", "kl": "kerala",
        "rajasthan": "rajasthan", "rj": "rajasthan",
        "uttar pradesh": "up", "up": "up",
        "madhya pradesh": "mp", "mp": "mp",
        "west bengal": "wb", "wb": "wb",
        "punjab": "punjab", "pb": "punjab",
        "haryana": "haryana", "hr": "haryana",
        "andhra pradesh": "andhra_pradesh", "ap": "andhra_pradesh",
    }
    return mapping.get(state.lower().strip(), "default")


@mcp.tool
async def get_labor_cost(
    trade: str,
    state: str,
    duration_days: int = 1,
    num_workers: int = 1,
    include_statutory: bool = True,
    include_overhead: bool = True,
) -> dict:
    """
    Get current labor cost for a specific trade in a given Indian state.

    Args:
        trade: Trade type. Options:
               'mason', 'carpenter', 'electrician', 'plumber', 'painter',
               'tile_layer', 'welder', 'fabricator', 'pool_specialist',
               'waterproofing_specialist', 'supervisor', 'project_manager',
               'unskilled', 'helper'
        state: Indian state e.g. 'Maharashtra', 'Karnataka', 'Delhi', 'Gujarat'
        duration_days: Number of working days
        num_workers: Number of workers of this trade
        include_statutory: Include PF (12%) + ESI (3.25%) + bonus (8.33%)
        include_overhead: Include contractor overhead/profit (18%)

    Returns:
        dict with daily_rate, all_in_rate, total_cost, full breakdown
    """
    state_key = normalize_state(state)
    trade_key = trade.lower().replace(" ", "_").replace("-", "_")

    trade_data = LABOR_RATES.get(trade_key, LABOR_RATES.get("unskilled", {}))
    daily_rate = trade_data.get(state_key, trade_data.get("default", 500))

    # Statutory costs
    pf = daily_rate * STATUTORY["pf_rate"] if include_statutory else 0
    esi = daily_rate * STATUTORY["esi_rate"] if include_statutory else 0
    bonus_daily = daily_rate * STATUTORY["bonus_rate"] if include_statutory else 0
    statutory_total = pf + esi + bonus_daily

    # Overhead
    subtotal = daily_rate + statutory_total
    overhead = subtotal * CONTRACTOR_OVERHEAD if include_overhead else 0

    all_in_daily = subtotal + overhead
    total_cost = all_in_daily * duration_days * num_workers

    return {
        "trade": trade,
        "state": state,
        "state_key": state_key,
        "num_workers": num_workers,
        "duration_days": duration_days,
        "daily_rate_base_inr": round(daily_rate),
        "statutory_breakdown": {
            "pf_12pct": round(pf),
            "esi_3_25pct": round(esi),
            "bonus_8_33pct": round(bonus_daily),
            "total_statutory": round(statutory_total),
        },
        "contractor_overhead_18pct": round(overhead),
        "all_in_daily_rate_inr": round(all_in_daily),
        "total_cost_inr": round(total_cost),
        "currency": "INR",
        "source": "schedule_of_rates_2024",
        "note": "Includes statutory obligations. Verify with state PWD schedule.",
    }


@mcp.tool
async def estimate_project_labor(
    project_type: str,
    area_sqft: float,
    state: str,
    duration_weeks: int,
    include_statutory: bool = True,
    include_overhead: bool = True,
) -> dict:
    """
    Estimate total labor cost for a full construction/interior project.

    Args:
        project_type: Type of project. Options:
                      'interior_fit_out', 'pool_construction', 'bathhouse_renovation',
                      'residential_construction', 'commercial_fit_out', 'pool_and_bathhouse'
        area_sqft: Total project area in square feet
        state: Indian state for wage rates
        duration_weeks: Estimated project duration in weeks
        include_statutory: Include PF + ESI + bonus
        include_overhead: Include contractor overhead

    Returns:
        Full labor cost breakdown by trade with grand total
    """
    duration_days = duration_weeks * 6  # 6-day construction week

    mix = TRADE_MIX.get(project_type, TRADE_MIX["interior_fit_out"])
    scale = area_sqft / 1000  # workers per 1000 sqft basis

    tasks = []
    trade_plan = {}

    for trade, workers_per_1k in mix.items():
        num_workers = max(1, round(workers_per_1k * scale))
        trade_plan[trade] = num_workers
        tasks.append(
            get_labor_cost(
                trade=trade,
                state=state,
                duration_days=duration_days,
                num_workers=num_workers,
                include_statutory=include_statutory,
                include_overhead=include_overhead,
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    breakdown = []
    grand_total = 0

    for r in results:
        if isinstance(r, Exception):
            continue
        breakdown.append(r)
        grand_total += r.get("total_cost_inr", 0)

    return {
        "project_type": project_type,
        "area_sqft": area_sqft,
        "state": state,
        "duration_weeks": duration_weeks,
        "duration_days": duration_days,
        "trade_breakdown": breakdown,
        "total_labor_cost_inr": round(grand_total),
        "labor_cost_per_sqft_inr": round(grand_total / area_sqft) if area_sqft else 0,
        "currency": "INR",
        "includes_statutory": include_statutory,
        "includes_overhead": include_overhead,
    }


@mcp.tool
async def get_labor_rates_for_state(state: str) -> dict:
    """
    Get all labor rates for a given state — useful for budgeting overview.

    Args:
        state: Indian state name e.g. 'Maharashtra', 'Karnataka', 'Delhi'

    Returns:
        dict of all trade daily rates for the state
    """
    state_key = normalize_state(state)
    rates = {}

    for trade, state_data in LABOR_RATES.items():
        rate = state_data.get(state_key, state_data.get("default", 0))
        rates[trade] = {
            "daily_rate_base": rate,
            "all_in_daily": round(
                rate * (1 + STATUTORY["pf_rate"] + STATUTORY["esi_rate"] +
                        STATUTORY["bonus_rate"]) * (1 + CONTRACTOR_OVERHEAD)
            ),
            "currency": "INR",
        }

    return {
        "state": state,
        "state_key": state_key,
        "rates": rates,
        "note": "All-in rate includes PF 12% + ESI 3.25% + bonus 8.33% + overhead 18%",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
