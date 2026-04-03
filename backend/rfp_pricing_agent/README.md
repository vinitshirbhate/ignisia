# RFP Pricing Agent — Dynamic Multi-MCP Cost Estimator

Simultaneously pulls real-time material prices, labor costs, GST rates,
and import duties using 4 parallel MCP servers.

---

## What it does

```
Input: RFP line items (materials, quantities)
         │
         ├── MCP Server 1: Material Prices  → IndiaMART live scraping + static fallback
         ├── MCP Server 2: Labor Costs      → State-wise PWD Schedule of Rates
         ├── MCP Server 3: GST & Tax        → GST 2.0 rates (Sep 2025) + ITC check
         └── MCP Server 4: Currency/Import  → Frankfurter live FX + customs duty
                   │
                   ▼
         Orchestrator (Claude claude-sonnet-4-6)
                   │
                   ▼
         Output: Complete cost breakdown JSON with grand total
```

All 4 servers run **simultaneously** — no sequential waiting.

---

## Prerequisites

- Python 3.11+
- Anthropic API key

No other paid APIs needed. Currency rates use Frankfurter (ECB, free).
GST rates are baked in (updated Sep 2025). Scraping uses httpx + bs4.

---

## Setup

```bash
# 1. Clone or unzip the project
cd rfp_pricing_agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

export ANTHROPIC_API_KEY=your_key_here
```

---

## Usage

### Option A: Run the full orchestrator

```bash
python orchestrator.py
```

This runs the example pool + bathhouse project from the Erwin Center Park RFP.

### Option B: Use individual servers directly

```python
import asyncio
from servers.material_prices_mcp import get_material_price, get_multiple_material_prices
from servers.labor_costs_mcp import estimate_project_labor
from servers.gst_mcp import calculate_gst_on_quote
from servers.currency_import_mcp import calculate_import_cost, get_exchange_rate

async def example():
    # Get price for plywood
    price = await get_material_price("plywood 18mm BWR", region="Mumbai")
    print(price)

    # Get USD→INR rate
    fx = await get_exchange_rate("USD", "INR", 1000)
    print(fx)

    # Calculate import cost
    import_cost = await calculate_import_cost(
        item="led lighting",
        fob_price_usd=50.0,
        quantity=40,
        origin_country="China",
    )
    print(import_cost)

asyncio.run(example())
```

### Option C: Custom RFP items

```python
from orchestrator import run_pricing_agent
import asyncio

result = asyncio.run(run_pricing_agent(
    rfp_items=[
        {"name": "cement OPC 53 grade", "quantity": 200, "unit": "bags"},
        {"name": "vitrified tiles 600x600", "quantity": 2000, "unit": "sqft"},
        {"name": "imported LED panel lights", "quantity": 30, "unit": "pieces"},
        {"name": "tmt steel Fe500", "quantity": 5, "unit": "MT"},
    ],
    region="Bangalore",
    state="Karnataka",
    project_type="commercial",
    area_sqft=5000,
    duration_weeks=12,
))

print(result)
```

### Run tests first

```bash
python tests/test_servers.py
```

---

## Project Structure

```
rfp_pricing_agent/
├── servers/
│   ├── material_prices_mcp.py   # MCP Server 1: Material market prices
│   ├── labor_costs_mcp.py       # MCP Server 2: Labor rates by state/trade
│   ├── gst_mcp.py               # MCP Server 3: GST rates (GST 2.0)
│   └── currency_import_mcp.py   # MCP Server 4: FX rates + import duties
├── tests/
│   └── test_servers.py          # Test all 4 servers independently
├── orchestrator.py              # Main agent that calls all servers in parallel
├── requirements.txt
├── .env.example
└── README.md
```

---

## MCP Server Tools Reference

### Server 1: Material Prices
| Tool | Description |
|------|-------------|
| `get_material_price` | Single material price with region adjustment |
| `get_multiple_material_prices` | Batch prices (parallel) — use this |

**Supported materials:** plywood, laminate, cement, steel, tiles (ceramic/vitrified),
paint, LED lights, PVC pipe, pool tiles, pool plaster, waterslide, pool pump,
pool filter, sanitaryware, CP fittings, roofing, glass, false ceiling, and more.

**Quality tiers:** `economy` | `standard` | `premium`

---

### Server 2: Labor Costs
| Tool | Description |
|------|-------------|
| `estimate_project_labor` | Full project labor estimate by type + area |
| `get_labor_cost` | Single trade cost with statutory add-ons |
| `get_labor_rates_for_state` | All trade rates for a state |

**Project types:** `interior_fit_out`, `pool_construction`, `bathhouse_renovation`,
`residential_construction`, `commercial_fit_out`, `pool_and_bathhouse`

**States supported:** Maharashtra, Karnataka, Delhi, Gujarat, Tamil Nadu,
Telangana, Kerala, Rajasthan, UP, MP, WB, Punjab, Haryana, Andhra Pradesh

**Includes:** PF 12% + ESI 3.25% + Bonus 8.33% + Contractor overhead 18%

---

### Server 3: GST & Tax
| Tool | Description |
|------|-------------|
| `calculate_gst_on_quote` | GST on full quote (parallel, use this) |
| `get_gst_rate` | Single item GST rate + ITC eligibility |
| `get_hsn_gst_rate` | Lookup by HSN code |

**GST regime:** GST 2.0 effective September 22, 2025
**Key rates:**
- Cement: 18% (was 28%)
- Steel/tiles/plywood/paint: 18%
- Sand/bricks: 5%
- LED lights: 12%
- Works contract (residential): 12%
- Works contract (commercial): 18%

---

### Server 4: Currency & Import
| Tool | Description |
|------|-------------|
| `get_exchange_rate` | Live FX via Frankfurter/ECB (free) |
| `get_multiple_exchange_rates` | Multiple currencies at once |
| `calculate_import_cost` | Full landed cost with all Indian duties |
| `compare_import_vs_domestic` | Import vs buying locally |

**Import duty calculation includes:**
- Basic Customs Duty (BCD): 7.5–40% depending on item
- Social Welfare Surcharge: 10% on BCD
- IGST: 12–28% on (CIF + BCD + SWS)
- CHA/Port charges: ~1.5% of CIF
- Last-mile delivery: ~3% of CIF

---

## Data Sources

| Data | Source | Live? |
|------|--------|-------|
| Material prices | IndiaMART scraping + static baseline | Best-effort live |
| Labor rates | State PWD Schedule of Rates 2024 | Static (annual update) |
| GST rates | GST 2.0 notification Sep 2025 | Static |
| Customs duties | Indian Customs Tariff 2024-25 | Static |
| Exchange rates | Frankfurter API (ECB) | Live ✓ |

---

## Limitations

1. **Material prices**: IndiaMART scraping may be blocked intermittently.
   Falls back to static baselines (2024 data). For production, subscribe to
   a commodities API.

2. **Labor rates**: Based on Schedule of Rates — actual market rates may vary
   by 10-20% depending on project urgency and availability.

3. **GST**: ITC eligibility rules are simplified. Consult a CA for complex
   project structures.

4. **Import duties**: Rates are for general goods. Special exemptions
   (EPCG, project imports) not included.

---

## Next Steps

- Connect to IndiaMART B2B API for authenticated pricing
- Add Redis caching for material prices (TTL: 24 hours)
- Add PDF report generation output
- Connect to your internal pricing database as a 5th MCP server
- Add competitor price comparison MCP server
