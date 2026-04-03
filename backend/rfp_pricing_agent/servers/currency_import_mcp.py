"""
MCP Server 4: Currency & Import Costs
Real-time exchange rates via Frankfurter API (ECB data, free, no key required).
Indian customs duty calculation for imported construction/interior materials.
"""

import logging
from fastmcp import FastMCP
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("currency_import")

mcp = FastMCP("Currency Import Server")

# ── Indian Import Duty Rates — Basic Customs Duty (BCD) + IGST ───────────────
# Source: Indian Customs Tariff 2024-25
IMPORT_DUTIES = {
    # Lighting
    "led_lighting":           {"bcd": 20.0,  "igst": 12, "sw_cess": 10, "chapter": "94"},
    "decorative_lighting":    {"bcd": 20.0,  "igst": 12, "sw_cess": 10, "chapter": "94"},
    "chandeliers":            {"bcd": 20.0,  "igst": 12, "sw_cess": 10, "chapter": "94"},
    "pendant_lights":         {"bcd": 20.0,  "igst": 12, "sw_cess": 10, "chapter": "94"},
    "track_lights":           {"bcd": 20.0,  "igst": 12, "sw_cess": 10, "chapter": "94"},
    # Pool equipment
    "pool_pumps":             {"bcd": 7.5,   "igst": 18, "sw_cess": 10, "chapter": "84"},
    "pool_filters":           {"bcd": 7.5,   "igst": 18, "sw_cess": 10, "chapter": "84"},
    "waterslides":            {"bcd": 10.0,  "igst": 18, "sw_cess": 10, "chapter": "95"},
    "water_features":         {"bcd": 10.0,  "igst": 18, "sw_cess": 10, "chapter": "84"},
    "pool_automation":        {"bcd": 7.5,   "igst": 18, "sw_cess": 10, "chapter": "90"},
    "pool_chemicals":         {"bcd": 10.0,  "igst": 18, "sw_cess": 10, "chapter": "28"},
    # Sanitaryware & fittings
    "premium_cp_fittings":    {"bcd": 10.0,  "igst": 18, "sw_cess": 10, "chapter": "84"},
    "premium_sanitaryware":   {"bcd": 10.0,  "igst": 18, "sw_cess": 10, "chapter": "69"},
    "premium_tiles":          {"bcd": 20.0,  "igst": 18, "sw_cess": 10, "chapter": "69"},
    "bathroom_accessories":   {"bcd": 20.0,  "igst": 18, "sw_cess": 10, "chapter": "73"},
    # Furniture & fittings
    "modular_kitchen":        {"bcd": 20.0,  "igst": 18, "sw_cess": 10, "chapter": "94"},
    "imported_furniture":     {"bcd": 20.0,  "igst": 18, "sw_cess": 10, "chapter": "94"},
    "hardware_fittings":      {"bcd": 7.5,   "igst": 18, "sw_cess": 10, "chapter": "83"},
    # Construction materials
    "marble_imported":        {"bcd": 40.0,  "igst": 12, "sw_cess": 10, "chapter": "25"},
    "granite_imported":       {"bcd": 30.0,  "igst": 12, "sw_cess": 10, "chapter": "25"},
    "premium_glass":          {"bcd": 10.0,  "igst": 18, "sw_cess": 10, "chapter": "70"},
    "aluminium_profiles":     {"bcd": 7.5,   "igst": 18, "sw_cess": 10, "chapter": "76"},
    # Electrical
    "premium_switchgear":     {"bcd": 7.5,   "igst": 18, "sw_cess": 10, "chapter": "85"},
    "building_automation":    {"bcd": 7.5,   "igst": 18, "sw_cess": 10, "chapter": "85"},
    # HVAC
    "hvac_equipment":         {"bcd": 7.5,   "igst": 18, "sw_cess": 10, "chapter": "84"},
    "vrf_system":             {"bcd": 7.5,   "igst": 28, "sw_cess": 10, "chapter": "84"},
    # Generic
    "general_goods":          {"bcd": 10.0,  "igst": 18, "sw_cess": 10, "chapter": "various"},
}

# Keyword → duty category mapping
KEYWORD_TO_DUTY = {
    "led": "led_lighting", "lighting": "led_lighting", "light": "led_lighting",
    "chandelier": "chandeliers", "pendant": "pendant_lights",
    "pump": "pool_pumps", "filter": "pool_filters",
    "waterslide": "waterslides", "slide": "waterslides",
    "water feature": "water_features", "geyser": "water_features",
    "cp fitting": "premium_cp_fittings", "faucet": "premium_cp_fittings",
    "tap": "premium_cp_fittings", "grohe": "premium_cp_fittings",
    "sanitaryware": "premium_sanitaryware", "kohler": "premium_sanitaryware",
    "tile": "premium_tiles", "marble": "marble_imported",
    "granite": "granite_imported", "glass": "premium_glass",
    "aluminium": "aluminium_profiles", "aluminum": "aluminium_profiles",
    "kitchen": "modular_kitchen", "furniture": "imported_furniture",
    "hardware": "hardware_fittings",
    "switchgear": "premium_switchgear",
    "hvac": "hvac_equipment", "ac": "hvac_equipment", "vrf": "vrf_system",
    "automation": "building_automation",
    "chemical": "pool_chemicals", "chlorine": "pool_chemicals",
}

# Fallback exchange rates (updated periodically)
FALLBACK_RATES = {
    "USD": {"INR": 84.5,  "EUR": 0.92,  "GBP": 0.79,  "AED": 3.67,  "CNY": 7.24},
    "EUR": {"INR": 92.0,  "USD": 1.09,  "GBP": 0.86,  "AED": 4.00,  "CNY": 7.88},
    "GBP": {"INR": 107.0, "USD": 1.27,  "EUR": 1.16,  "AED": 4.66,  "CNY": 9.16},
    "AED": {"INR": 23.0,  "USD": 0.27,  "EUR": 0.25,  "GBP": 0.21,  "CNY": 1.97},
    "CNY": {"INR": 11.7,  "USD": 0.138, "EUR": 0.127, "GBP": 0.109, "AED": 0.508},
    "SGD": {"INR": 63.0,  "USD": 0.745, "EUR": 0.685},
    "JPY": {"INR": 0.56,  "USD": 0.0067},
    "AUD": {"INR": 55.0,  "USD": 0.65},
    "CAD": {"INR": 62.0,  "USD": 0.74},
}


def resolve_duty_category(item: str) -> tuple[str, dict]:
    """Resolve item name to import duty category."""
    item_lower = item.lower()
    key = item_lower.replace(" ", "_").replace("-", "_")

    if key in IMPORT_DUTIES:
        return key, IMPORT_DUTIES[key]

    for kw, duty_key in KEYWORD_TO_DUTY.items():
        if kw in item_lower:
            return duty_key, IMPORT_DUTIES[duty_key]

    return "general_goods", IMPORT_DUTIES["general_goods"]


@mcp.tool
async def get_exchange_rate(
    from_currency: str = "USD",
    to_currency: str = "INR",
    amount: float = 1.0,
) -> dict:
    """
    Get real-time currency exchange rate.
    Uses Frankfurter API (ECB data, free, no API key needed).

    Args:
        from_currency: Source currency ISO code e.g. 'USD', 'EUR', 'GBP',
                       'AED', 'CNY', 'SGD', 'JPY', 'AUD', 'CAD'
        to_currency: Target currency ISO code e.g. 'INR', 'USD', 'EUR'
        amount: Amount to convert (default 1.0)

    Returns:
        dict with live rate, converted amount, source, and date
    """
    from_upper = from_currency.upper().strip()
    to_upper = to_currency.upper().strip()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.frankfurter.app/latest",
                params={"from": from_upper, "to": to_upper},
            )

            if resp.status_code == 200:
                data = resp.json()
                rate = data["rates"].get(to_upper)

                if rate:
                    return {
                        "from_currency": from_upper,
                        "to_currency": to_upper,
                        "rate": round(rate, 4),
                        "amount": amount,
                        "converted_amount": round(amount * rate, 2),
                        "date": data.get("date", "live"),
                        "source": "Frankfurter API (ECB)",
                        "is_live": True,
                    }

    except Exception as e:
        logger.warning(f"Live FX fetch failed: {e}")

    # Fallback to static rates
    rate = (
        FALLBACK_RATES
        .get(from_upper, {})
        .get(to_upper, 1.0)
    )

    return {
        "from_currency": from_upper,
        "to_currency": to_upper,
        "rate": rate,
        "amount": amount,
        "converted_amount": round(amount * rate, 2),
        "date": "static_fallback",
        "source": "static_rates (live fetch failed)",
        "is_live": False,
        "note": "Use live data for final quotations",
    }


@mcp.tool
async def get_multiple_exchange_rates(
    base_currency: str = "USD",
    target_currencies: list[str] | None = None,
) -> dict:
    """
    Get exchange rates for multiple target currencies at once.

    Args:
        base_currency: Source currency e.g. 'USD'
        target_currencies: List of targets e.g. ['INR', 'EUR', 'GBP', 'AED']
                           Defaults to ['INR', 'EUR', 'GBP', 'AED', 'CNY', 'SGD']

    Returns:
        dict with all rates from the base currency
    """
    if target_currencies is None:
        target_currencies = ["INR", "EUR", "GBP", "AED", "CNY", "SGD"]

    targets_str = ",".join(t.upper() for t in target_currencies)
    base_upper = base_currency.upper()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.frankfurter.app/latest",
                params={"from": base_upper, "to": targets_str},
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "base_currency": base_upper,
                    "rates": data["rates"],
                    "date": data.get("date"),
                    "source": "Frankfurter API (ECB)",
                    "is_live": True,
                }
    except Exception as e:
        logger.warning(f"Multi-rate fetch failed: {e}")

    fallback = FALLBACK_RATES.get(base_upper, {})
    return {
        "base_currency": base_upper,
        "rates": {t: fallback.get(t, 1.0) for t in target_currencies},
        "date": "static_fallback",
        "source": "static_rates",
        "is_live": False,
    }


@mcp.tool
async def calculate_import_cost(
    item: str,
    fob_price_usd: float,
    quantity: int = 1,
    origin_country: str = "China",
    shipping_mode: str = "sea",
    include_last_mile: bool = True,
) -> dict:
    """
    Calculate total landed cost in INR for an imported item, including all duties.

    Args:
        item: Item description e.g. 'led lighting', 'waterslide', 'pool pump',
              'premium cp fittings', 'imported marble', 'modular kitchen'
        fob_price_usd: FOB price per unit in USD (price at origin port)
        quantity: Number of units
        origin_country: Country of manufacture e.g. 'China', 'Italy',
                        'Germany', 'USA', 'UAE', 'Turkey'
        shipping_mode: 'sea' (cheaper, slower) or 'air' (expensive, fast)
        include_last_mile: Include Indian port-to-site delivery charges

    Returns:
        Full landed cost breakdown with all duties, taxes, and freight in INR
    """
    # Get live exchange rate
    fx = await get_exchange_rate("USD", "INR", 1.0)
    usd_to_inr = fx["rate"]

    # Get duty category
    duty_cat, duty_info = resolve_duty_category(item)

    # FOB calculation
    fob_total_usd = fob_price_usd * quantity

    # Freight estimates by shipping mode and origin
    transit_days_map = {
        ("sea", "china"): 25, ("sea", "india"): 0,
        ("sea", "italy"): 45, ("sea", "germany"): 45,
        ("sea", "usa"): 35,   ("sea", "uae"): 12,
        ("sea", "turkey"): 30,
        ("air", "china"): 5,  ("air", "italy"): 4,
        ("air", "germany"): 4, ("air", "usa"): 6,
        ("air", "uae"): 3,    ("air", "turkey"): 4,
    }

    freight_pct_map = {
        "sea": 0.08,   # 8% of FOB for sea freight
        "air": 0.22,   # 22% of FOB for air freight
    }

    origin_lower = origin_country.lower()
    transit_days = transit_days_map.get(
        (shipping_mode.lower(), origin_lower), 30
    )
    freight_pct = freight_pct_map.get(shipping_mode.lower(), 0.08)

    freight_usd = fob_total_usd * freight_pct
    insurance_usd = fob_total_usd * 0.005  # 0.5% of FOB (CIF standard)
    cif_usd = fob_total_usd + freight_usd + insurance_usd
    cif_inr = cif_usd * usd_to_inr

    # ── Duty calculation ──────────────────────────────────────────────────────
    # Step 1: Basic Customs Duty (BCD) on CIF
    bcd_pct = duty_info["bcd"]
    bcd_amount = cif_inr * (bcd_pct / 100)

    # Step 2: Social Welfare Surcharge (SWS) — 10% on BCD
    sw_cess_pct = duty_info["sw_cess"]
    sw_cess_amount = bcd_amount * (sw_cess_pct / 100)

    # Step 3: IGST on (CIF + BCD + SWS)
    igst_pct = duty_info["igst"]
    igst_base = cif_inr + bcd_amount + sw_cess_amount
    igst_amount = igst_base * (igst_pct / 100)

    # Step 4: Customs handling + CHA charges (~1.5% of CIF)
    cha_charges = cif_inr * 0.015

    # Step 5: Last-mile delivery (port to site in India)
    last_mile = cif_inr * 0.03 if include_last_mile else 0  # ~3% of CIF

    # ── Grand total ───────────────────────────────────────────────────────────
    total_duty_inr = bcd_amount + sw_cess_amount + igst_amount
    total_landed_inr = (
        cif_inr + total_duty_inr + cha_charges + last_mile
    )
    landed_per_unit_inr = total_landed_inr / quantity
    effective_duty_pct = (total_duty_inr / cif_inr) * 100 if cif_inr else 0

    return {
        "item": item,
        "duty_category": duty_cat,
        "origin_country": origin_country,
        "shipping_mode": shipping_mode,
        "quantity": quantity,
        "transit_days": transit_days,

        "fob_section": {
            "fob_per_unit_usd": fob_price_usd,
            "fob_total_usd": round(fob_total_usd, 2),
            "freight_usd": round(freight_usd, 2),
            "insurance_usd": round(insurance_usd, 2),
            "cif_total_usd": round(cif_usd, 2),
        },

        "forex": {
            "usd_to_inr_rate": usd_to_inr,
            "cif_inr": round(cif_inr),
            "fx_source": fx["source"],
            "fx_live": fx["is_live"],
        },

        "duties_inr": {
            "basic_customs_duty_pct": bcd_pct,
            "bcd_amount": round(bcd_amount),
            "social_welfare_surcharge_pct": f"10% on BCD",
            "sw_cess_amount": round(sw_cess_amount),
            "igst_pct": igst_pct,
            "igst_base": round(igst_base),
            "igst_amount": round(igst_amount),
            "total_duty": round(total_duty_inr),
            "effective_duty_pct": round(effective_duty_pct, 1),
        },

        "other_charges_inr": {
            "cha_clearing_charges": round(cha_charges),
            "last_mile_delivery": round(last_mile),
        },

        "summary_inr": {
            "total_landed_cost": round(total_landed_inr),
            "landed_cost_per_unit": round(landed_per_unit_inr),
            "cost_vs_fob_multiple": round(total_landed_inr / (fob_total_usd * usd_to_inr), 2),
        },
        "currency": "INR",
    }


@mcp.tool
async def compare_import_vs_domestic(
    item: str,
    domestic_price_inr: float,
    import_fob_usd: float,
    quantity: int = 1,
    origin_country: str = "China",
) -> dict:
    """
    Compare cost of importing an item vs buying domestically.
    Helps decide whether premium imports are worth it.

    Args:
        item: Item description e.g. 'led chandelier', 'premium cp fittings'
        domestic_price_inr: Current Indian market price per unit in INR
        import_fob_usd: FOB price per unit in USD if importing
        quantity: Number of units
        origin_country: Country to import from

    Returns:
        Comparison showing which option is cheaper and by how much
    """
    # Get import cost
    import_result = await calculate_import_cost(
        item=item,
        fob_price_usd=import_fob_usd,
        quantity=quantity,
        origin_country=origin_country,
    )

    import_per_unit = import_result["summary_inr"]["landed_cost_per_unit"]
    domestic_total = domestic_price_inr * quantity
    import_total = import_result["summary_inr"]["total_landed_cost"]

    saving_per_unit = domestic_price_inr - import_per_unit
    saving_total = domestic_total - import_total
    saving_pct = (saving_per_unit / domestic_price_inr * 100) if domestic_price_inr else 0

    recommendation = "domestic" if domestic_price_inr <= import_per_unit else "import"

    return {
        "item": item,
        "quantity": quantity,
        "domestic": {
            "price_per_unit_inr": domestic_price_inr,
            "total_cost_inr": round(domestic_total),
            "lead_time": "immediate",
        },
        "import": {
            "fob_per_unit_usd": import_fob_usd,
            "landed_per_unit_inr": import_per_unit,
            "total_landed_cost_inr": import_total,
            "lead_time_days": import_result["transit_days"],
            "origin": origin_country,
        },
        "comparison": {
            "saving_per_unit_inr": round(saving_per_unit),
            "saving_total_inr": round(saving_total),
            "saving_pct": round(saving_pct, 1),
            "recommendation": recommendation,
            "reason": (
                f"Import saves ₹{abs(round(saving_per_unit))}/unit "
                f"({abs(round(saving_pct, 1))}%) but takes "
                f"{import_result['transit_days']} days"
                if recommendation == "import"
                else f"Domestic is cheaper by ₹{abs(round(saving_per_unit))}/unit"
            ),
        },
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
