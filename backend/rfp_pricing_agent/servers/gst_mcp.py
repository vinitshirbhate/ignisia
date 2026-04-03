"""
MCP Server 3: GST & Tax
Provides GST rates for construction materials and services in India.
Updated to GST 2.0 rates effective September 22, 2025.
"""

import asyncio
import logging
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gst")

mcp = FastMCP("GST Tax Server")

# ── GST Rate Table — GST 2.0 effective Sep 22, 2025 ──────────────────────────
GST_RATES = {
    # ── Construction materials ────────────────────────────────────────────────
    "cement":                       {"rate": 18, "hsn": "2523", "cat": "material"},
    "cement_opc":                   {"rate": 18, "hsn": "2523", "cat": "material"},
    "cement_ppc":                   {"rate": 18, "hsn": "2523", "cat": "material"},
    "sand":                         {"rate": 5,  "hsn": "2505", "cat": "material"},
    "aggregate":                    {"rate": 5,  "hsn": "2517", "cat": "material"},
    "gravel":                       {"rate": 5,  "hsn": "2517", "cat": "material"},
    "bricks_clay":                  {"rate": 5,  "hsn": "6901", "cat": "material"},
    "bricks_fly_ash":               {"rate": 5,  "hsn": "6815", "cat": "material"},
    "bricks_sand_lime":             {"rate": 5,  "hsn": "6901", "cat": "material"},
    "aac_block":                    {"rate": 5,  "hsn": "6810", "cat": "material"},
    "concrete_block":               {"rate": 12, "hsn": "6810", "cat": "material"},
    "steel":                        {"rate": 18, "hsn": "7213", "cat": "material"},
    "tmt_bars":                     {"rate": 18, "hsn": "7214", "cat": "material"},
    "steel_rod":                    {"rate": 18, "hsn": "7213", "cat": "material"},
    "ms_plate":                     {"rate": 18, "hsn": "7208", "cat": "material"},
    "galvanized_pipe":              {"rate": 18, "hsn": "7306", "cat": "material"},
    "tiles_ceramic":                {"rate": 18, "hsn": "6907", "cat": "material"},
    "tiles_vitrified":              {"rate": 18, "hsn": "6907", "cat": "material"},
    "tiles_porcelain":              {"rate": 18, "hsn": "6907", "cat": "material"},
    "pool_tile":                    {"rate": 18, "hsn": "6907", "cat": "material"},
    "marble":                       {"rate": 12, "hsn": "2516", "cat": "material"},
    "granite":                      {"rate": 12, "hsn": "2516", "cat": "material"},
    "marble_finished":              {"rate": 28, "hsn": "6802", "cat": "material"},
    "paint":                        {"rate": 18, "hsn": "3209", "cat": "material"},
    "primer":                       {"rate": 18, "hsn": "3208", "cat": "material"},
    "plywood":                      {"rate": 18, "hsn": "4412", "cat": "material"},
    "laminate":                     {"rate": 18, "hsn": "4823", "cat": "material"},
    "mdf":                          {"rate": 18, "hsn": "4411", "cat": "material"},
    "hardboard":                    {"rate": 18, "hsn": "4411", "cat": "material"},
    "pvc_pipe":                     {"rate": 18, "hsn": "3917", "cat": "material"},
    "upvc_pipe":                    {"rate": 18, "hsn": "3917", "cat": "material"},
    "cpvc_pipe":                    {"rate": 18, "hsn": "3917", "cat": "material"},
    "hdpe_pipe":                    {"rate": 18, "hsn": "3917", "cat": "material"},
    "glass":                        {"rate": 18, "hsn": "7003", "cat": "material"},
    "toughened_glass":              {"rate": 18, "hsn": "7007", "cat": "material"},
    "aluminium_section":            {"rate": 18, "hsn": "7604", "cat": "material"},
    "gypsum_board":                 {"rate": 18, "hsn": "6809", "cat": "material"},
    "pop":                          {"rate": 18, "hsn": "2520", "cat": "material"},
    "waterproofing_compound":       {"rate": 18, "hsn": "3214", "cat": "material"},
    "pool_plaster":                 {"rate": 18, "hsn": "3214", "cat": "material"},
    "adhesive":                     {"rate": 18, "hsn": "3506", "cat": "material"},
    "tile_adhesive":                {"rate": 18, "hsn": "3824", "cat": "material"},
    "grout":                        {"rate": 18, "hsn": "3824", "cat": "material"},
    "insulation":                   {"rate": 18, "hsn": "6806", "cat": "material"},
    "roofing_sheet":                {"rate": 18, "hsn": "7210", "cat": "material"},
    "wire_mesh":                    {"rate": 18, "hsn": "7314", "cat": "material"},
    "chain_link_fencing":           {"rate": 18, "hsn": "7314", "cat": "material"},

    # ── Electrical materials ──────────────────────────────────────────────────
    "electrical_wire":              {"rate": 18, "hsn": "8544", "cat": "electrical"},
    "electrical_cable":             {"rate": 18, "hsn": "8544", "cat": "electrical"},
    "switchgear":                   {"rate": 18, "hsn": "8536", "cat": "electrical"},
    "mcb":                          {"rate": 18, "hsn": "8536", "cat": "electrical"},
    "distribution_board":           {"rate": 18, "hsn": "8537", "cat": "electrical"},
    "conduit_pipe":                 {"rate": 18, "hsn": "3917", "cat": "electrical"},
    "earthing_material":            {"rate": 18, "hsn": "8544", "cat": "electrical"},

    # ── Lighting ──────────────────────────────────────────────────────────────
    "led_light":                    {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "led_panel":                    {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "led_strip":                    {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "downlight":                    {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "spotlight":                    {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "chandelier":                   {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "decorative_light":             {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "street_light":                 {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "floodlight":                   {"rate": 12, "hsn": "9405", "cat": "lighting"},
    "imported_light":               {"rate": 18, "hsn": "9405", "cat": "lighting",
                                     "note": "Higher rate for imported fixtures"},

    # ── Sanitaryware & fittings ───────────────────────────────────────────────
    "sanitaryware":                 {"rate": 18, "hsn": "6910", "cat": "sanitary"},
    "wc":                           {"rate": 18, "hsn": "6910", "cat": "sanitary"},
    "washbasin":                    {"rate": 18, "hsn": "6910", "cat": "sanitary"},
    "urinal":                       {"rate": 18, "hsn": "6910", "cat": "sanitary"},
    "cp_fittings":                  {"rate": 18, "hsn": "8481", "cat": "sanitary"},
    "tap":                          {"rate": 18, "hsn": "8481", "cat": "sanitary"},
    "faucet":                       {"rate": 18, "hsn": "8481", "cat": "sanitary"},
    "shower":                       {"rate": 18, "hsn": "8481", "cat": "sanitary"},
    "bathroom_accessories":         {"rate": 18, "hsn": "7324", "cat": "sanitary"},
    "flush_valve":                  {"rate": 18, "hsn": "8481", "cat": "sanitary"},

    # ── Pool equipment ────────────────────────────────────────────────────────
    "pool_pump":                    {"rate": 18, "hsn": "8413", "cat": "pool"},
    "pool_filter":                  {"rate": 18, "hsn": "8421", "cat": "pool"},
    "pool_chemical":                {"rate": 18, "hsn": "2801", "cat": "pool"},
    "chlorinator":                  {"rate": 18, "hsn": "8421", "cat": "pool"},
    "pool_heater":                  {"rate": 18, "hsn": "8419", "cat": "pool"},
    "waterslide":                   {"rate": 18, "hsn": "9508", "cat": "pool"},
    "water_feature":                {"rate": 18, "hsn": "8413", "cat": "pool"},
    "pool_ladder":                  {"rate": 18, "hsn": "7308", "cat": "pool"},
    "pool_light":                   {"rate": 18, "hsn": "9405", "cat": "pool"},
    "pool_geyser":                  {"rate": 18, "hsn": "8413", "cat": "pool"},
    "pool_automation":              {"rate": 18, "hsn": "9031", "cat": "pool"},
    "bulkhead_fitting":             {"rate": 18, "hsn": "3926", "cat": "pool"},

    # ── Services ──────────────────────────────────────────────────────────────
    "works_contract_residential":   {"rate": 12, "hsn": "9954", "cat": "service"},
    "works_contract_commercial":    {"rate": 18, "hsn": "9954", "cat": "service"},
    "works_contract_government":    {"rate": 12, "hsn": "9954", "cat": "service"},
    "labor_contractor":             {"rate": 18, "hsn": "9986", "cat": "service"},
    "architectural_services":       {"rate": 18, "hsn": "9983", "cat": "service"},
    "engineering_services":         {"rate": 18, "hsn": "9983", "cat": "service"},
    "project_management":           {"rate": 18, "hsn": "9983", "cat": "service"},
    "interior_design":              {"rate": 18, "hsn": "9983", "cat": "service"},
    "transport":                    {"rate": 5,  "hsn": "9965", "cat": "service"},
    "equipment_hire":               {"rate": 18, "hsn": "9973", "cat": "service"},
    "survey":                       {"rate": 18, "hsn": "9983", "cat": "service"},
    "testing_inspection":           {"rate": 18, "hsn": "9983", "cat": "service"},
}

# Keyword → GST item mapping
KEYWORD_MAP = {
    "cement": "cement", "opc": "cement_opc", "ppc": "cement_ppc",
    "sand": "sand", "aggregate": "aggregate", "gravel": "gravel",
    "brick": "bricks_clay", "fly ash": "bricks_fly_ash", "aac": "aac_block",
    "steel": "steel", "tmt": "tmt_bars", "rebar": "tmt_bars",
    "tile": "tiles_ceramic", "vitrified": "tiles_vitrified",
    "pool tile": "pool_tile", "marble": "marble", "granite": "granite",
    "paint": "paint", "primer": "primer",
    "plywood": "plywood", "laminate": "laminate", "mdf": "mdf",
    "pvc": "pvc_pipe", "upvc": "upvc_pipe", "cpvc": "cpvc_pipe",
    "glass": "glass", "toughened": "toughened_glass",
    "aluminium": "aluminium_section", "aluminum": "aluminium_section",
    "gypsum": "gypsum_board", "pop": "pop",
    "waterproof": "waterproofing_compound", "plaster": "pool_plaster",
    "wire": "electrical_wire", "cable": "electrical_cable",
    "switchgear": "switchgear", "mcb": "mcb",
    "led": "led_light", "panel light": "led_panel", "downlight": "downlight",
    "chandelier": "chandelier", "decorative light": "decorative_light",
    "imported light": "imported_light",
    "sanitaryware": "sanitaryware", "wc": "wc", "commode": "wc",
    "washbasin": "washbasin", "tap": "tap", "faucet": "faucet",
    "shower": "shower", "cp fitting": "cp_fittings", "bathroom": "bathroom_accessories",
    "pump": "pool_pump", "filter": "pool_filter", "chlorinator": "chlorinator",
    "waterslide": "waterslide", "slide": "waterslide",
    "water feature": "water_feature", "geyser": "pool_geyser",
    "pool ladder": "pool_ladder",
    "works contract": "works_contract_commercial",
    "labor": "labor_contractor", "labour": "labor_contractor",
    "architect": "architectural_services", "design": "interior_design",
    "engineering": "engineering_services", "transport": "transport",
    "roofing": "roofing_sheet", "fencing": "chain_link_fencing",
}


def resolve_item(item: str) -> tuple[str, dict]:
    """Resolve item name to GST rate entry."""
    item_lower = item.lower()

    # Direct match
    if item_lower in GST_RATES:
        return item_lower, GST_RATES[item_lower]

    # Normalized key match
    item_key = item_lower.replace(" ", "_").replace("-", "_")
    if item_key in GST_RATES:
        return item_key, GST_RATES[item_key]

    # Keyword match
    for kw, gst_key in KEYWORD_MAP.items():
        if kw in item_lower and gst_key in GST_RATES:
            return gst_key, GST_RATES[gst_key]

    # Partial match in keys
    for key, val in GST_RATES.items():
        if key in item_key or item_key in key:
            return key, val

    return "unknown", {"rate": 18, "hsn": "unknown", "cat": "general"}


@mcp.tool
async def get_gst_rate(
    item: str,
    project_type: str = "commercial",
    is_government_project: bool = False,
) -> dict:
    """
    Get GST rate for a construction material or service.

    Args:
        item: Material or service name. Examples:
              'cement', 'plywood', 'led_light', 'pool_pump',
              'works_contract_residential', 'labor_contractor',
              'waterslide', 'vitrified tiles', 'imported light'
        project_type: 'residential', 'commercial', 'government', 'infrastructure'
        is_government_project: Government projects may qualify for reduced rates

    Returns:
        dict with gst_rate, hsn_code, itc_eligible, cgst, sgst, effective_rate
    """
    resolved_key, gst_info = resolve_item(item)
    rate = gst_info["rate"]

    # Government project adjustments
    if is_government_project and gst_info["cat"] == "service":
        rate = 12
        project_note = "Reduced 12% for government works contracts"
    elif project_type == "residential" and gst_info["cat"] == "service":
        rate = 12
        project_note = "12% for residential works contracts"
    else:
        project_note = f"Standard rate for {project_type} project"

    # ITC eligibility
    itc_eligible = True
    itc_restriction = None

    if project_type == "residential" and gst_info["cat"] == "material":
        itc_eligible = False
        itc_restriction = (
            "ITC blocked under Sec 17(5)(c) CGST Act "
            "for construction of immovable property for personal use"
        )
    elif gst_info["cat"] == "service" and project_type == "residential":
        itc_eligible = False
        itc_restriction = "ITC blocked for residential works contract services"

    return {
        "item": item,
        "resolved_as": resolved_key,
        "hsn_code": gst_info["hsn"],
        "category": gst_info["cat"],
        "gst_rate_pct": rate,
        "cgst_pct": rate / 2,
        "sgst_pct": rate / 2,
        "igst_pct": rate,
        "itc_eligible": itc_eligible,
        "itc_restriction": itc_restriction,
        "project_type": project_type,
        "project_note": project_note,
        "note": gst_info.get("note", ""),
        "effective_date": "2025-09-22",
        "regime": "GST 2.0",
    }


@mcp.tool
async def calculate_gst_on_quote(
    line_items: list[dict],
    project_type: str = "commercial",
    is_government_project: bool = False,
) -> dict:
    """
    Calculate GST for an entire quotation with multiple line items simultaneously.

    Args:
        line_items: List of dicts, each with:
                    - item (str): Material or service name
                    - quantity (float): Quantity
                    - unit_price (float): Price per unit in INR (ex-GST)
                    - unit (str, optional): Unit of measurement
        project_type: 'residential', 'commercial', 'government'
        is_government_project: Applies reduced rates for government work

    Returns:
        Full quotation with GST breakdown per line item and grand total

    Example:
        line_items = [
            {"item": "cement", "quantity": 200, "unit_price": 380, "unit": "bags"},
            {"item": "plywood", "quantity": 2000, "unit_price": 75, "unit": "sqft"},
            {"item": "led panel light", "quantity": 30, "unit_price": 900, "unit": "pieces"},
        ]
    """
    # Fetch all GST rates in parallel
    gst_tasks = [
        get_gst_rate(li["item"], project_type, is_government_project)
        for li in line_items
    ]
    gst_results = await asyncio.gather(*gst_tasks)

    detailed = []
    total_base = 0.0
    total_gst = 0.0
    total_amount = 0.0
    total_itc_available = 0.0

    for li, gst in zip(line_items, gst_results):
        base = li["quantity"] * li["unit_price"]
        gst_amt = base * (gst["gst_rate_pct"] / 100)
        line_total = base + gst_amt
        itc = gst_amt if gst["itc_eligible"] else 0.0

        detailed.append({
            "item": li["item"],
            "quantity": li["quantity"],
            "unit": li.get("unit", ""),
            "unit_price_ex_gst": li["unit_price"],
            "base_amount": round(base),
            "hsn_code": gst["hsn_code"],
            "gst_rate_pct": gst["gst_rate_pct"],
            "cgst_amount": round(gst_amt / 2),
            "sgst_amount": round(gst_amt / 2),
            "total_gst_amount": round(gst_amt),
            "line_total_incl_gst": round(line_total),
            "itc_eligible": gst["itc_eligible"],
            "itc_amount": round(itc),
            "itc_restriction": gst.get("itc_restriction"),
        })

        total_base += base
        total_gst += gst_amt
        total_amount += line_total
        total_itc_available += itc

    effective_rate = (total_gst / total_base * 100) if total_base else 0

    return {
        "project_type": project_type,
        "is_government_project": is_government_project,
        "line_items": detailed,
        "totals": {
            "subtotal_ex_gst": round(total_base),
            "total_cgst": round(total_gst / 2),
            "total_sgst": round(total_gst / 2),
            "total_gst": round(total_gst),
            "grand_total_incl_gst": round(total_amount),
            "total_itc_available": round(total_itc_available),
            "net_cost_after_itc": round(total_amount - total_itc_available),
            "effective_gst_rate_pct": round(effective_rate, 2),
        },
        "currency": "INR",
        "gst_regime": "GST 2.0 (effective Sep 22, 2025)",
    }


@mcp.tool
async def get_hsn_gst_rate(hsn_code: str) -> dict:
    """
    Look up GST rate by HSN code directly.

    Args:
        hsn_code: HSN code e.g. '2523' for cement, '4412' for plywood,
                  '9405' for lighting, '8413' for pumps

    Returns:
        dict with applicable GST rate and typical items under this HSN
    """
    hsn_map = {
        "2523": {"rate": 18, "description": "Cement and clinker"},
        "2505": {"rate": 5,  "description": "Natural sand"},
        "2517": {"rate": 5,  "description": "Pebbles, gravel, aggregate"},
        "6901": {"rate": 5,  "description": "Clay bricks, blocks"},
        "6815": {"rate": 5,  "description": "Fly ash bricks"},
        "6810": {"rate": 12, "description": "Concrete articles (blocks, tiles)"},
        "7213": {"rate": 18, "description": "Steel bars and rods"},
        "7214": {"rate": 18, "description": "TMT bars"},
        "6907": {"rate": 18, "description": "Ceramic and vitrified tiles"},
        "2516": {"rate": 12, "description": "Marble and granite blocks"},
        "6802": {"rate": 28, "description": "Worked marble, granite"},
        "3209": {"rate": 18, "description": "Water-based paints and coatings"},
        "3208": {"rate": 18, "description": "Primer and surface coatings"},
        "4412": {"rate": 18, "description": "Plywood"},
        "4411": {"rate": 18, "description": "MDF, hardboard"},
        "4823": {"rate": 18, "description": "Laminate sheets"},
        "3917": {"rate": 18, "description": "PVC, UPVC, CPVC pipes"},
        "7003": {"rate": 18, "description": "Float glass"},
        "7007": {"rate": 18, "description": "Toughened/tempered glass"},
        "7604": {"rate": 18, "description": "Aluminium bars, rods, sections"},
        "6809": {"rate": 18, "description": "Gypsum board"},
        "2520": {"rate": 18, "description": "Plaster of Paris"},
        "3214": {"rate": 18, "description": "Waterproofing compound, pool plaster"},
        "8544": {"rate": 18, "description": "Wires and cables"},
        "8536": {"rate": 18, "description": "Electrical switchgear, MCBs"},
        "8537": {"rate": 18, "description": "Distribution boards"},
        "9405": {"rate": 12, "description": "Lamps, lighting fittings"},
        "6910": {"rate": 18, "description": "Sanitaryware — WC, washbasin"},
        "8481": {"rate": 18, "description": "Taps, faucets, valves, CP fittings"},
        "7324": {"rate": 18, "description": "Bathroom accessories"},
        "8413": {"rate": 18, "description": "Pumps (pool, water)"},
        "8421": {"rate": 18, "description": "Filter machinery"},
        "2801": {"rate": 18, "description": "Pool chemicals, chlorine"},
        "9508": {"rate": 18, "description": "Waterslides, amusement park rides"},
        "9954": {"rate": 18, "description": "Construction works contract services"},
        "9986": {"rate": 18, "description": "Labour contractor services"},
        "9983": {"rate": 18, "description": "Professional services (arch/eng)"},
        "9965": {"rate": 5,  "description": "Goods transport services"},
        "7210": {"rate": 18, "description": "Galvanised/roofing sheets"},
        "7314": {"rate": 18, "description": "Fencing, wire mesh"},
    }

    info = hsn_map.get(hsn_code)
    if not info:
        return {
            "hsn_code": hsn_code,
            "error": "HSN code not found in database",
            "suggestion": "Verify on CBIC portal: https://cbic-gst.gov.in",
        }

    return {
        "hsn_code": hsn_code,
        "gst_rate_pct": info["rate"],
        "cgst_pct": info["rate"] / 2,
        "sgst_pct": info["rate"] / 2,
        "description": info["description"],
        "effective_date": "2025-09-22",
        "source": "GST 2.0 notification",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
