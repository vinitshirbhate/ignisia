"""
Test suite for all 4 MCP servers.
Run this to verify each server works before running the full orchestrator.

Usage:
    python tests/test_servers.py
"""

import asyncio
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Test Material Prices ──────────────────────────────────────────────────────
async def test_material_prices():
    print("\n[1/4] Testing Material Prices Server...")
    from servers.material_prices_mcp import get_material_price, get_multiple_material_prices

    # Single material
    result = await get_material_price("plywood 18mm BWR", region="Mumbai")
    assert "price_avg" in result, "Missing price_avg"
    assert result["currency"] == "INR", "Wrong currency"
    print(f"  ✓ Plywood 18mm: ₹{result['price_avg']} {result['unit']}")

    # Multiple materials in parallel
    result = await get_multiple_material_prices(
        materials=[
            {"name": "cement OPC 53 grade", "quantity": 100},
            {"name": "vitrified tiles 600x600", "quantity": 500, "quality_tier": "standard"},
            {"name": "led panel light 36W", "quantity": 20},
        ],
        region="Delhi",
    )
    assert "results" in result, "Missing results"
    assert len(result["results"]) == 3, "Wrong number of results"
    print(f"  ✓ Multiple materials: ₹{result['summary']['total_cost_avg_inr']:,} total")

    # Unknown material falls back gracefully
    result = await get_material_price("nonexistent_material_xyz")
    assert "error" in result or "price_avg" in result, "Should handle unknown gracefully"
    print(f"  ✓ Unknown material handled gracefully")

    print("  ✅ Material Prices Server PASSED")
    return True


# ── Test Labor Costs ──────────────────────────────────────────────────────────
async def test_labor_costs():
    print("\n[2/4] Testing Labor Costs Server...")
    from servers.labor_costs_mcp import get_labor_cost, estimate_project_labor, get_labor_rates_for_state

    # Single trade
    result = await get_labor_cost("mason", "Maharashtra", duration_days=30, num_workers=5)
    assert "total_cost_inr" in result, "Missing total_cost_inr"
    assert result["total_cost_inr"] > 0, "Cost should be positive"
    print(f"  ✓ Mason (5 workers, 30 days, Maharashtra): ₹{result['total_cost_inr']:,}")

    # Full project estimate
    result = await estimate_project_labor(
        project_type="pool_and_bathhouse",
        area_sqft=10000,
        state="Maharashtra",
        duration_weeks=16,
    )
    assert "total_labor_cost_inr" in result, "Missing total"
    assert result["total_labor_cost_inr"] > 0, "Total should be positive"
    print(f"  ✓ Pool+bathhouse 10k sqft 16wks: ₹{result['total_labor_cost_inr']:,}")
    print(f"    Per sqft: ₹{result['labor_cost_per_sqft_inr']}")

    # State rates overview
    result = await get_labor_rates_for_state("Karnataka")
    assert "rates" in result, "Missing rates"
    assert "mason" in result["rates"], "Missing mason rate"
    print(f"  ✓ Karnataka mason all-in: ₹{result['rates']['mason']['all_in_daily']}/day")

    print("  ✅ Labor Costs Server PASSED")
    return True


# ── Test GST ──────────────────────────────────────────────────────────────────
async def test_gst():
    print("\n[3/4] Testing GST Server...")
    from servers.gst_mcp import get_gst_rate, calculate_gst_on_quote, get_hsn_gst_rate

    # Single item rate
    result = await get_gst_rate("cement")
    assert result["gst_rate_pct"] == 18, f"Cement should be 18%, got {result['gst_rate_pct']}"
    print(f"  ✓ Cement GST: {result['gst_rate_pct']}% (HSN: {result['hsn_code']})")

    result = await get_gst_rate("led panel light")
    assert result["gst_rate_pct"] == 12, f"LED should be 12%, got {result['gst_rate_pct']}"
    print(f"  ✓ LED panel GST: {result['gst_rate_pct']}% (HSN: {result['hsn_code']})")

    result = await get_gst_rate("sand")
    assert result["gst_rate_pct"] == 5, f"Sand should be 5%, got {result['gst_rate_pct']}"
    print(f"  ✓ Sand GST: {result['gst_rate_pct']}%")

    # Full quote calculation
    result = await calculate_gst_on_quote(
        line_items=[
            {"item": "cement", "quantity": 100, "unit_price": 380, "unit": "bags"},
            {"item": "plywood", "quantity": 500, "unit_price": 75, "unit": "sqft"},
            {"item": "led panel", "quantity": 20, "unit_price": 900, "unit": "pieces"},
            {"item": "waterslide", "quantity": 1, "unit_price": 400000, "unit": "unit"},
        ],
        project_type="commercial",
    )
    assert "totals" in result, "Missing totals"
    assert result["totals"]["grand_total_incl_gst"] > 0, "Grand total should be positive"
    print(f"  ✓ Quote GST calculation: ₹{result['totals']['total_gst']:,} GST")
    print(f"    Grand total: ₹{result['totals']['grand_total_incl_gst']:,}")

    # HSN lookup
    result = await get_hsn_gst_rate("9405")
    assert result["gst_rate_pct"] == 12, "HSN 9405 (lighting) should be 12%"
    print(f"  ✓ HSN 9405: {result['gst_rate_pct']}% - {result['description']}")

    print("  ✅ GST Server PASSED")
    return True


# ── Test Currency & Import ────────────────────────────────────────────────────
async def test_currency_import():
    print("\n[4/4] Testing Currency & Import Server...")
    from servers.currency_import_mcp import (
        get_exchange_rate, get_multiple_exchange_rates,
        calculate_import_cost, compare_import_vs_domestic,
    )

    # Exchange rate
    result = await get_exchange_rate("USD", "INR", 100.0)
    assert "converted_amount" in result, "Missing converted_amount"
    assert result["converted_amount"] > 0, "Should convert to positive INR"
    print(f"  ✓ USD→INR: 1 USD = ₹{result['rate']} (source: {result['source']})")

    # Multiple rates
    result = await get_multiple_exchange_rates("USD", ["INR", "EUR", "GBP"])
    assert "rates" in result, "Missing rates"
    assert "INR" in result["rates"], "Missing INR"
    print(f"  ✓ Multi-rate: INR={result['rates']['INR']}, EUR={result['rates']['EUR']}")

    # Import cost calculation
    result = await calculate_import_cost(
        item="led lighting",
        fob_price_usd=50.0,
        quantity=40,
        origin_country="China",
        shipping_mode="sea",
    )
    assert "summary_inr" in result, "Missing summary_inr"
    assert result["summary_inr"]["total_landed_cost"] > 0, "Landed cost should be positive"
    print(f"  ✓ Import 40x LED (China sea): ₹{result['summary_inr']['total_landed_cost']:,}")
    print(f"    Per unit landed: ₹{result['summary_inr']['landed_cost_per_unit']:,}")
    print(f"    Effective duty: {result['duties_inr']['effective_duty_pct']}%")

    # Compare import vs domestic
    result = await compare_import_vs_domestic(
        item="led chandelier",
        domestic_price_inr=8000,
        import_fob_usd=60.0,
        quantity=10,
        origin_country="China",
    )
    assert "comparison" in result, "Missing comparison"
    print(f"  ✓ Import vs domestic: {result['comparison']['recommendation'].upper()}")
    print(f"    {result['comparison']['reason']}")

    print("  ✅ Currency & Import Server PASSED")
    return True


# ── Run all tests ─────────────────────────────────────────────────────────────
async def run_all_tests():
    print("=" * 60)
    print("RFP PRICING AGENT — SERVER TEST SUITE")
    print("=" * 60)

    tests = [
        ("Material Prices", test_material_prices),
        ("Labor Costs",     test_labor_costs),
        ("GST",             test_gst),
        ("Currency/Import", test_currency_import),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            await test_fn()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("All tests passed! Ready to run orchestrator.py")
    else:
        print(f"{failed} test(s) failed. Fix errors before running orchestrator.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
