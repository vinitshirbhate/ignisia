"""
RFP Pricing Orchestrator
Runs all 4 MCP servers simultaneously and synthesizes a complete cost breakdown.
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("orchestrator")
client = OpenAI(
    base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# ── Server configurations ─────────────────────────────────────────────────────
SERVERS = {
    "materials": StdioServerParameters(
        command=sys.executable,
        args=["servers/material_prices_mcp.py"],
    ),
    "labor": StdioServerParameters(
        command=sys.executable,
        args=["servers/labor_costs_mcp.py"],
    ),
    "gst": StdioServerParameters(
        command=sys.executable,
        args=["servers/gst_mcp.py"],
    ),
    "currency": StdioServerParameters(
        command=sys.executable,
        args=["servers/currency_import_mcp.py"],
    ),
}

SYSTEM_PROMPT = """You are an expert construction cost estimation agent for India.

You have access to 4 specialized live data tools:

1. **materials__*** — Real-time market prices for construction materials
   - get_material_price: Single material price
   - get_multiple_material_prices: Multiple materials simultaneously (PREFER THIS)

2. **labor__*** — Labor costs by trade and Indian state
   - estimate_project_labor: Full project labor estimate (USE THIS FIRST)
   - get_labor_cost: Individual trade cost
   - get_labor_rates_for_state: All trades for a state

3. **gst__*** — GST rates and tax calculations (GST 2.0, Sep 2025)
   - calculate_gst_on_quote: GST on entire line item list (PREFER THIS)
   - get_gst_rate: Single item GST rate
   - get_hsn_gst_rate: Lookup by HSN code

4. **currency__*** — Exchange rates and import duty calculations
   - get_exchange_rate: Live currency conversion
   - calculate_import_cost: Full landed cost for imported items
   - compare_import_vs_domestic: Import vs domestic cost comparison

## CRITICAL RULES:
- ALWAYS call tools in PARALLEL, never sequentially
- Use batch tools (get_multiple_material_prices, calculate_gst_on_quote) over individual calls
- For imported/premium items, ALWAYS calculate import costs
- Include GST on every line item
- Add 3-5% contingency on total
- Output a structured JSON cost breakdown

## Output Format:
Always return a valid JSON with:
- project_summary
- material_costs (with GST)
- labor_costs
- import_costs (if applicable)
- summary_totals
- cost_per_sqft
- contingency
- grand_total
"""


async def collect_all_tools(sessions: dict[str, ClientSession]) -> list[dict]:
    """Collect tools from all MCP servers in parallel."""
    async def get_tools(server_name: str, session: ClientSession) -> list[dict]:
        resp = await session.list_tools()
        tools = []
        for tool in resp.tools:
            tools.append({
                "name": f"{server_name}__{tool.name}",
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
                "_server": server_name,
                "_tool": tool.name,
            })
        return tools

    results = await asyncio.gather(
        *[get_tools(name, session) for name, session in sessions.items()]
    )
    all_tools = []
    for tool_list in results:
        all_tools.extend(tool_list)

    logger.info(f"Collected {len(all_tools)} tools from {len(sessions)} servers")
    return all_tools


async def call_tool_parallel(
    sessions: dict[str, ClientSession],
    tool_calls: list[Any],
) -> list[tuple[str, Any]]:
    """Execute all tool calls in parallel across servers."""
    async def single_call(tc):
        server_name = tc.function.name.split("__")[0]
        tool_name = tc.function.name.split("__")[1]
        session = sessions[server_name]

        try:
            arguments = json.loads(tc.function.arguments)
            result = await session.call_tool(tool_name, arguments=arguments)
            content = result.content[0].text if result.content else "{}"
            logger.info(f"  ✓ {tc.function.name}")
            return tc.id, content
        except Exception as e:
            logger.error(f"  ✗ {tc.function.name}: {e}")
            return tc.id, json.dumps({"error": str(e)})

    results = await asyncio.gather(*[single_call(tc) for tc in tool_calls])
    return list(results)


async def run_pricing_agent(
    rfp_items: list[dict],
    region: str = "Mumbai",
    state: str = "Maharashtra",
    project_type: str = "commercial",
    area_sqft: float = 1000.0,
    duration_weeks: int = 8,
    is_government_project: bool = False,
) -> dict:
    """
    Main agent runner — connects to all 4 MCP servers and orchestrates cost estimation.

    Args:
        rfp_items: List of items from the RFP with name, quantity, unit
        region: City for material price lookup
        state: State for labor rate lookup
        project_type: 'residential', 'commercial', 'government'
        area_sqft: Total project area
        duration_weeks: Estimated construction duration
        is_government_project: Apply government GST rates

    Returns:
        Complete cost breakdown as dict
    """
    async with (
        stdio_client(SERVERS["materials"]) as (r1, w1),
        stdio_client(SERVERS["labor"])     as (r2, w2),
        stdio_client(SERVERS["gst"])       as (r3, w3),
        stdio_client(SERVERS["currency"])  as (r4, w4),
    ):
        async with (
            ClientSession(r1, w1) as s1,
            ClientSession(r2, w2) as s2,
            ClientSession(r3, w3) as s3,
            ClientSession(r4, w4) as s4,
        ):
            sessions = {
                "materials": s1,
                "labor":     s2,
                "gst":       s3,
                "currency":  s4,
            }

            # Initialize all sessions with logging and timeout
            logger.info("Initializing all MCP servers...")
            async def init_with_timeout(name, session):
                logger.info(f"[{name}] Starting initialization...")
                try:
                    await asyncio.wait_for(session.initialize(), timeout=15.0)
                    logger.info(f"[{name}] Initialization complete.")
                except TimeoutError:
                    logger.error(f"[{name}] Initialization TIMED OUT after 15 seconds.")
                except Exception as e:
                    logger.error(f"[{name}] Initialization ERROR: {e}")
            
            await asyncio.gather(*[init_with_timeout(name, s) for name, s in sessions.items()])
            logger.info("All servers ready (or timed out).")

            # Collect all tools
            all_tools = await collect_all_tools(sessions)

            # Format tools for OpenAI API
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["input_schema"],
                    }
                }
                for t in all_tools
            ]

            # Build the user message
            user_message = f"""
Provide a complete cost breakdown for this construction/interior project:

PROJECT DETAILS:
- Region: {region}
- State (for labor): {state}
- Project type: {project_type}
- Area: {area_sqft} sqft
- Duration: {duration_weeks} weeks
- Government project: {is_government_project}

ITEMS FROM RFP:
{json.dumps(rfp_items, indent=2)}

REQUIRED ANALYSIS:
1. Fetch current market prices for ALL materials listed above
2. Calculate labor costs for {state} for a {project_type} project of {area_sqft} sqft
3. Calculate GST on each line item (project_type: {project_type})
4. For any imported/premium items (imported lights, slides, premium fittings), 
   calculate full import duty and landed cost
5. Get USD/INR exchange rate for import calculations
6. Synthesize into a complete cost breakdown with grand total

Call tools in PARALLEL. Return structured JSON.
"""

            messages = [{"role": "user", "content": user_message}]
            final_result = {}
            iteration = 0
            max_iterations = 5

            # ── Agentic loop ──────────────────────────────────────────────────────
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Agent iteration {iteration}")

                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                    tools=openai_tools,
                )

                choice = response.choices[0]
                logger.info(f"Stop reason: {choice.finish_reason}")

                if choice.finish_reason == "stop" or choice.finish_reason == "length" or not choice.message.tool_calls:
                    text = choice.message.content or ""
                    text = text.strip()
                    # Try to parse as JSON
                    try:
                        # Find JSON block if wrapped in markdown
                        if "```json" in text:
                            start = text.find("```json") + 7
                            end = text.find("```", start)
                            text = text[start:end].strip()
                        elif "```" in text:
                            start = text.find("```") + 3
                            end = text.find("```", start)
                            text = text[start:end].strip()
                        final_result = json.loads(text)
                    except json.JSONDecodeError:
                        final_result = {"raw_response": text}
                    break

                if choice.message.tool_calls:
                    tool_calls = choice.message.tool_calls

                    logger.info(f"Calling {len(tool_calls)} tools in parallel:")
                    for tc in tool_calls:
                        logger.info(f"  → {tc.function.name}")

                    # Execute ALL tool calls simultaneously
                    results = await call_tool_parallel(sessions, tool_calls)

                    # Add assistant response and tool results to messages
                    messages.append(choice.message.model_dump(exclude_unset=True))

                    for tool_id, result_text in results:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": result_text,
                        })

            return final_result


# ── CLI entry point ───────────────────────────────────────────────────────────
async def main():
    """Example run with pool + bathhouse RFP items."""
    rfp_items = [
        # Pool materials
        {"name": "reinforced concrete (pool shell)", "quantity": 150, "unit": "cubic meters"},
        {"name": "pool tile anti-slip 300x300",      "quantity": 1800, "unit": "sqft"},
        {"name": "pool plaster white waterproof",    "quantity": 1800, "unit": "sqft"},
        {"name": "pool pump 2HP centrifugal",        "quantity": 2,    "unit": "pieces"},
        {"name": "pool sand filter",                 "quantity": 2,    "unit": "pieces"},
        {"name": "pool chemical chlorinator",        "quantity": 1,    "unit": "set"},
        {"name": "waterslide double loop FRP",       "quantity": 1,    "unit": "unit"},
        {"name": "water feature geyser set",         "quantity": 3,    "unit": "sets"},
        {"name": "schedule 40 PVC pipe 4 inch",      "quantity": 200,  "unit": "meters"},
        {"name": "pool fencing chain link",          "quantity": 300,  "unit": "sqft"},
        # Bathhouse materials
        {"name": "cement OPC 53 grade",              "quantity": 300,  "unit": "50kg bags"},
        {"name": "vitrified tiles 600x600",          "quantity": 2500, "unit": "sqft"},
        {"name": "sanitaryware set",                 "quantity": 10,   "unit": "sets"},
        {"name": "cp fittings premium",              "quantity": 10,   "unit": "sets"},
        {"name": "tmt steel bars Fe500",             "quantity": 5,    "unit": "MT"},
        {"name": "plywood 18mm BWR grade",           "quantity": 800,  "unit": "sqft"},
        {"name": "gypsum board false ceiling",       "quantity": 2250, "unit": "sqft"},
        {"name": "exterior paint weathershield",     "quantity": 200,  "unit": "litres"},
        {"name": "imported LED panel lights 36W",    "quantity": 40,   "unit": "pieces"},
        {"name": "electrical wiring and switchgear", "quantity": 1,    "unit": "lot"},
    ]

    print("\n" + "=" * 60)
    print("RFP PRICING AGENT — PARALLEL MCP EXECUTION")
    print("=" * 60)
    print(f"Project: Erwin Center Pool & Bathhouse")
    print(f"Items: {len(rfp_items)} line items")
    print(f"Region: Gastonia NC → India analog: Mumbai, Maharashtra")
    print("=" * 60 + "\n")

    result = await run_pricing_agent(
        rfp_items=rfp_items,
        region="Mumbai",
        state="Maharashtra",
        project_type="commercial",
        area_sqft=10011.0,  # 7761 pool deck + 2250 bathhouse
        duration_weeks=16,
        is_government_project=False,
    )

    print("\n" + "=" * 60)
    print("COST BREAKDOWN RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


if __name__ == "__main__":
    asyncio.run(main())
