"""
MCP Server 1: Material Prices
Fetches current market prices for construction and interior materials.
Falls back to static baseline rates if live scraping fails.
"""

import asyncio
import re
import logging
from datetime import datetime
from fastmcp import FastMCP
import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("material_prices")

mcp = FastMCP("Material Prices Server")

# ── Static baseline prices (INR) — updated periodically ──────────────────────
MATERIAL_BASELINES = {
    "plywood": {
        "economy":  {"min": 35,  "max": 60,   "unit": "per sqft", "note": "12mm MR grade"},
        "standard": {"min": 55,  "max": 90,   "unit": "per sqft", "note": "18mm BWR grade"},
        "premium":  {"min": 85,  "max": 140,  "unit": "per sqft", "note": "18mm Marine/BWP"},
    },
    "laminate": {
        "economy":  {"min": 500,  "max": 900,  "unit": "per sheet", "note": "0.8mm"},
        "standard": {"min": 800,  "max": 1400, "unit": "per sheet", "note": "1mm standard"},
        "premium":  {"min": 1400, "max": 2800, "unit": "per sheet", "note": "1mm branded"},
    },
    "cement": {
        "economy":  {"min": 340, "max": 370, "unit": "per 50kg bag"},
        "standard": {"min": 360, "max": 400, "unit": "per 50kg bag"},
        "premium":  {"min": 390, "max": 430, "unit": "per 50kg bag", "note": "OPC 53 grade"},
    },
    "steel": {
        "standard": {"min": 56000, "max": 65000, "unit": "per MT", "note": "TMT Fe500"},
        "premium":  {"min": 62000, "max": 72000, "unit": "per MT", "note": "TMT Fe550"},
    },
    "tiles_ceramic": {
        "economy":  {"min": 25,  "max": 45,  "unit": "per sqft"},
        "standard": {"min": 40,  "max": 80,  "unit": "per sqft"},
        "premium":  {"min": 75,  "max": 150, "unit": "per sqft"},
    },
    "tiles_vitrified": {
        "economy":  {"min": 40,  "max": 70,  "unit": "per sqft"},
        "standard": {"min": 65,  "max": 120, "unit": "per sqft"},
        "premium":  {"min": 110, "max": 220, "unit": "per sqft"},
    },
    "paint": {
        "economy":  {"min": 150, "max": 220, "unit": "per litre", "note": "Asian/Berger economy"},
        "standard": {"min": 220, "max": 320, "unit": "per litre", "note": "Asian Royale/Dulux"},
        "premium":  {"min": 300, "max": 500, "unit": "per litre", "note": "Dulux Weathershield"},
    },
    "led_light": {
        "economy":  {"min": 300,  "max": 600,  "unit": "per piece", "note": "No-brand LED panel"},
        "standard": {"min": 600,  "max": 1200, "unit": "per piece", "note": "Havells/Philips"},
        "premium":  {"min": 1200, "max": 3500, "unit": "per piece", "note": "Imported/Osram"},
    },
    "pvc_pipe": {
        "standard": {"min": 180, "max": 280, "unit": "per 3m length", "note": "4 inch SCH40"},
    },
    "pool_tile": {
        "standard": {"min": 80,  "max": 150, "unit": "per sqft", "note": "Anti-slip pool tiles"},
        "premium":  {"min": 140, "max": 280, "unit": "per sqft", "note": "Imported pool tiles"},
    },
    "pool_plaster": {
        "standard": {"min": 45,  "max": 75,  "unit": "per sqft", "note": "White plaster finish"},
        "premium":  {"min": 70,  "max": 120, "unit": "per sqft", "note": "Quartz plaster"},
    },
    "waterslide": {
        "standard": {"min": 250000, "max": 450000, "unit": "per unit", "note": "Single loop FRP"},
        "premium":  {"min": 400000, "max": 800000, "unit": "per unit", "note": "Double loop"},
    },
    "pool_pump": {
        "standard": {"min": 18000, "max": 35000, "unit": "per unit", "note": "1-2 HP centrifugal"},
        "premium":  {"min": 32000, "max": 65000, "unit": "per unit", "note": "Variable speed"},
    },
    "pool_filter": {
        "standard": {"min": 12000, "max": 28000, "unit": "per unit", "note": "Sand filter"},
        "premium":  {"min": 25000, "max": 55000, "unit": "per unit", "note": "Cartridge filter"},
    },
    "sanitaryware": {
        "economy":  {"min": 3000,  "max": 6000,  "unit": "per set", "note": "Parryware/Hindware"},
        "standard": {"min": 6000,  "max": 15000, "unit": "per set", "note": "Cera/Jaquar"},
        "premium":  {"min": 15000, "max": 45000, "unit": "per set", "note": "Kohler/American Standard"},
    },
    "cp_fittings": {
        "economy":  {"min": 1500, "max": 3000,  "unit": "per set"},
        "standard": {"min": 3000, "max": 8000,  "unit": "per set", "note": "Jaquar/Hindware"},
        "premium":  {"min": 7000, "max": 25000, "unit": "per set", "note": "Grohe/Hansgrohe"},
    },
    "roofing_sheet": {
        "standard": {"min": 280, "max": 420, "unit": "per sqft", "note": "Galvalume"},
        "premium":  {"min": 380, "max": 600, "unit": "per sqft", "note": "Insulated sandwich"},
    },
    "aluminum_partition": {
        "standard": {"min": 450, "max": 750,  "unit": "per sqft"},
        "premium":  {"min": 700, "max": 1200, "unit": "per sqft", "note": "System partition"},
    },
    "glass": {
        "standard": {"min": 70,  "max": 130, "unit": "per sqft", "note": "5mm clear toughened"},
        "premium":  {"min": 120, "max": 250, "unit": "per sqft", "note": "8mm toughened/DGU"},
    },
    "false_ceiling": {
        "economy":  {"min": 45,  "max": 75,  "unit": "per sqft", "note": "Gypsum board basic"},
        "standard": {"min": 70,  "max": 120, "unit": "per sqft", "note": "Gypsum with grid"},
        "premium":  {"min": 110, "max": 200, "unit": "per sqft", "note": "Designer/POP"},
    },
}

# Material category keyword mapping
CATEGORY_MAP = {
    "plywood": ["plywood", "ply", "bwr", "bwp", "marine"],
    "laminate": ["laminate", "formica", "sunmica", "laminates"],
    "cement": ["cement", "opc", "ppc", "portland"],
    "steel": ["steel", "tmt", "rebar", "reinforcement", "iron rod"],
    "tiles_ceramic": ["ceramic tile", "floor tile", "wall tile"],
    "tiles_vitrified": ["vitrified", "polished tile", "double charged"],
    "paint": ["paint", "emulsion", "primer", "enamel", "weathershield"],
    "led_light": ["led", "light", "lamp", "panel light", "downlight", "spotlight"],
    "pvc_pipe": ["pvc pipe", "upvc", "cpvc", "hdpe pipe"],
    "pool_tile": ["pool tile", "swimming pool tile", "anti-slip"],
    "pool_plaster": ["plaster", "pool plaster", "waterproof plaster"],
    "waterslide": ["water slide", "waterslide", "slide", "double loop"],
    "pool_pump": ["pump", "pool pump", "centrifugal pump"],
    "pool_filter": ["filter", "sand filter", "pool filter"],
    "sanitaryware": ["sanitaryware", "wc", "commode", "washbasin", "urinal"],
    "cp_fittings": ["cp fitting", "tap", "faucet", "shower", "mixer"],
    "roofing_sheet": ["roofing", "roof sheet", "galvalume", "metal roof"],
    "aluminum_partition": ["partition", "aluminium", "aluminum", "dry wall"],
    "glass": ["glass", "toughened", "tempered", "dgu"],
    "false_ceiling": ["false ceiling", "gypsum", "pop ceiling", "grid ceiling"],
}


def find_category(material: str) -> str | None:
    """Match material name to a category key."""
    m_lower = material.lower()
    for category, keywords in CATEGORY_MAP.items():
        if any(kw in m_lower for kw in keywords):
            return category
    return None


@mcp.tool
async def get_material_price(
    material: str,
    unit: str = "auto",
    region: str = "India",
    quality_tier: str = "standard"
) -> dict:
    """
    Fetch current market price for a construction or interior material.

    Args:
        material: Material name e.g. 'plywood 18mm BWR', 'laminate sheet 1mm',
                  'cement OPC 50kg', 'LED panel light 36W', 'vitrified tiles 600x600'
        unit: Unit of measurement. Use 'auto' to detect from material name.
              Options: 'per sqft', 'per piece', 'per bag', 'per kg', 'per MT',
                       'per sheet', 'per litre', 'per unit', 'per set'
        region: City or state for regional pricing e.g. 'Mumbai', 'Delhi', 'Bangalore'
        quality_tier: 'economy', 'standard', or 'premium'

    Returns:
        dict with price_min, price_max, price_avg, unit, source, currency
    """
    category = find_category(material)
    tier_data = None

    if category and category in MATERIAL_BASELINES:
        cat_data = MATERIAL_BASELINES[category]
        tier_data = cat_data.get(quality_tier, cat_data.get("standard"))

    # Try live scraping IndiaMART
    live_prices = []
    search_query = f"{material} price {region}"

    try:
        async with httpx.AsyncClient(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-IN,en;q=0.5",
            },
            timeout=12.0,
            follow_redirects=True,
        ) as client:
            url = (
                "https://dir.indiamart.com/search.mp"
                f"?ss={search_query.replace(' ', '+')}"
            )
            resp = await client.get(url)

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # IndiaMART price selectors
                for selector in [".price", ".prc", "[class*='price']", ".rate"]:
                    elems = soup.select(selector)
                    for elem in elems[:15]:
                        text = elem.get_text(strip=True)
                        nums = re.findall(r"[\d,]+", text.replace(",", ""))
                        for n in nums:
                            try:
                                p = int(n)
                                if 10 < p < 2_000_000:
                                    live_prices.append(p)
                            except ValueError:
                                pass

    except Exception as e:
        logger.warning(f"Live scrape failed for '{material}': {e}")

    # Build response
    if live_prices and len(live_prices) >= 2:
        # Filter outliers (remove top and bottom 10%)
        live_prices.sort()
        trim = max(1, len(live_prices) // 10)
        trimmed = live_prices[trim:-trim] if len(live_prices) > 4 else live_prices
        price_min = min(trimmed)
        price_max = max(trimmed)
        price_avg = sum(trimmed) // len(trimmed)
        detected_unit = tier_data["unit"] if tier_data else unit
        source = "indiamart_live"
        confidence = "high"
        note = f"Live data — {len(live_prices)} listings scraped"
    elif tier_data:
        price_min = tier_data["min"]
        price_max = tier_data["max"]
        price_avg = (price_min + price_max) // 2
        detected_unit = tier_data["unit"]
        source = "static_baseline_2024"
        confidence = "medium"
        note = tier_data.get("note", "Static baseline — live fetch unavailable")
    else:
        return {
            "material": material,
            "error": "Material not found in database and live fetch failed",
            "suggestion": (
                "Try more specific name e.g. 'plywood 18mm BWR grade', "
                "'OPC cement 50kg bag', 'LED panel 36W'"
            ),
        }

    # Regional adjustment (approximate multipliers)
    regional_multipliers = {
        "mumbai": 1.15, "delhi": 1.10, "bangalore": 1.08,
        "chennai": 1.05, "hyderabad": 1.05, "pune": 1.08,
        "kolkata": 1.02, "ahmedabad": 0.98, "jaipur": 0.95,
        "india": 1.0,
    }
    multiplier = regional_multipliers.get(region.lower(), 1.0)

    return {
        "material": material,
        "category": category or "unknown",
        "quality_tier": quality_tier,
        "price_min": round(price_min * multiplier),
        "price_max": round(price_max * multiplier),
        "price_avg": round(price_avg * multiplier),
        "unit": detected_unit if unit == "auto" else unit,
        "currency": "INR",
        "region": region,
        "regional_multiplier": multiplier,
        "source": source,
        "confidence": confidence,
        "note": note,
        "fetched_at": datetime.utcnow().isoformat(),
    }


@mcp.tool
async def get_multiple_material_prices(
    materials: list[dict],
    region: str = "India",
) -> dict:
    """
    Fetch prices for multiple materials simultaneously (parallel).

    Args:
        materials: List of dicts, each with:
                   - name (str): Material name
                   - unit (str, optional): Unit of measurement
                   - quality_tier (str, optional): 'economy'|'standard'|'premium'
                   - quantity (float, optional): Quantity needed
        region: City or state for regional pricing

    Returns:
        dict with results list and total_estimated_cost

    Example:
        materials = [
            {"name": "plywood 18mm BWR", "unit": "per sqft", "quantity": 2000},
            {"name": "laminate 1mm standard", "unit": "per sheet", "quantity": 150},
        ]
    """
    tasks = [
        get_material_price(
            material=m["name"],
            unit=m.get("unit", "auto"),
            region=region,
            quality_tier=m.get("quality_tier", "standard"),
        )
        for m in materials
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = []
    total_min = 0
    total_max = 0
    total_avg = 0

    for i, (m, r) in enumerate(zip(materials, results)):
        if isinstance(r, Exception):
            output.append({"material": m["name"], "error": str(r)})
            continue

        quantity = m.get("quantity", 1)
        line_min = r.get("price_min", 0) * quantity
        line_max = r.get("price_max", 0) * quantity
        line_avg = r.get("price_avg", 0) * quantity

        total_min += line_min
        total_max += line_max
        total_avg += line_avg

        output.append({
            **r,
            "quantity": quantity,
            "line_cost_min": round(line_min),
            "line_cost_max": round(line_max),
            "line_cost_avg": round(line_avg),
        })

    return {
        "region": region,
        "results": output,
        "summary": {
            "total_items": len(output),
            "total_cost_min_inr": round(total_min),
            "total_cost_max_inr": round(total_max),
            "total_cost_avg_inr": round(total_avg),
            "currency": "INR",
        },
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
