import os
import json
import re
import requests
import fitz
import shutil
import math
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# ─── ENV LOADER ───────────────────────────────────────────────────────────────
def load_env():
    env = Path(__file__).with_name(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()

# ─── APP SETUP ────────────────────────────────────────────────────────────────
app = FastAPI(title="AI_Validate – Proposal Intelligence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ─── PROMPTS ──────────────────────────────────────────────────────────────────

CHUNK_EXTRACTOR_PROMPT = """You are an expert document parser for business proposals, RFPs, and technical documents.
Your job is to extract structured facts from a chunk of proposal text.

Extract ALL of the following that appear in the text:
- Monetary values / costs / prices (with context)
- Percentages and ratios
- Dates, durations, and timelines
- Quantities and numeric claims
- Named deliverables, milestones, and phases
- Stated assumptions or constraints
- Compliance or regulatory references
- Any mathematical calculations or formulas mentioned

Return ONLY valid JSON in this format:
{
  "monetary_items": [{"value": number, "currency": "USD", "context": "description", "raw": "original text"}],
  "percentages": [{"value": number, "context": "description", "raw": "original text"}],
  "dates_timelines": [{"label": "string", "duration_days": number_or_null, "raw": "original text"}],
  "numeric_claims": [{"value": number, "unit": "string", "context": "description", "raw": "original text"}],
  "deliverables": ["list of deliverable names"],
  "assumptions": ["list of stated assumptions"],
  "compliance_refs": ["regulatory or compliance references"],
  "calculations": [{"expression": "string", "claimed_result": "string", "raw": "original text"}]
}
If none exist for a category, return an empty list."""


VALIDATOR_PROMPT = """You are a senior proposal validation expert and business analyst.
You have been given structured data extracted from a business proposal document.

Your job is to perform a DEEP, CRITICAL review and identify ALL issues. Be thorough and specific.

VALIDATION TASKS:
1. **Calculation Errors**: Check all numbers, totals, subtotals, margins, percentages. Verify math is correct.
2. **Pricing Review**: Are prices reasonable? Any missing line items? Inconsistent pricing across sections? Hidden costs?
3. **Logic Flaws**: Does the proposal logic hold together? Contradictions? Circular reasoning?
4. **Completeness Check**: Are deliverables fully defined? Are timelines realistic? Are assumptions valid?
5. **Inconsistencies**: Do numbers match across sections? Do dates align? Do totals add up?
6. **Risky Decisions**: Flag overly aggressive timelines, underpriced items, vague scope, missing compliance items.
7. **Missing Elements**: What critical information is absent that should be in a proposal?

EXTRACTED DATA:
{extracted_data}

FULL DOCUMENT TEXT (first 8000 chars for context):
{doc_text_preview}

Return ONLY valid JSON in this format:
{
  "overall_score": <0-100 integer, 100=perfect>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "executive_summary": "<2-3 sentence summary of overall proposal health>",
  "issues": [
    {
      "id": "ISSUE-001",
      "severity": "<CRITICAL|HIGH|MEDIUM|LOW|INFO>",
      "category": "<CALCULATION|PRICING|LOGIC|COMPLETENESS|INCONSISTENCY|RISK|MISSING>",
      "title": "<short title>",
      "description": "<detailed explanation of the issue>",
      "evidence": "<exact text or numbers from the document that support this finding>",
      "recommendation": "<specific actionable fix>",
      "impact": "<what happens if this is not fixed>"
    }
  ],
  "strengths": ["<things the proposal does well>"],
  "missing_sections": ["<sections typically required but absent>"],
  "calculation_verification": [
    {
      "expression": "<what was calculated>",
      "claimed": "<what document says>",
      "verified": "<correct value>",
      "status": "<CORRECT|INCORRECT|UNVERIFIABLE>"
    }
  ],
  "pricing_analysis": {
    "total_found": <total monetary value found or null>,
    "currency": "USD",
    "concerns": ["<pricing concerns>"],
    "missing_costs": ["<costs likely missing>"]
  }
}"""


# ─── PDF EXTRACTION ───────────────────────────────────────────────────────────

def extract_text_with_pages(pdf_path: Path) -> list[dict]:
    """Extract text per page with page numbers."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = " ".join(page.get_text("text").split())
        if text.strip():
            pages.append({"page": i + 1, "text": text})
    return pages


def chunk_pages(pages: list[dict], chunk_size: int = 3) -> list[dict]:
    """Group pages into chunks for parallel extraction."""
    chunks = []
    for i in range(0, len(pages), chunk_size):
        batch = pages[i:i + chunk_size]
        combined = " ".join(p["text"] for p in batch)
        chunks.append({
            "pages": f"{batch[0]['page']}-{batch[-1]['page']}",
            "text": combined
        })
    return chunks


# ─── LLM CALLS ────────────────────────────────────────────────────────────────

def call_llm(system: str, user: str, model: str = None, json_mode: bool = True) -> dict | str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in .env")

    selected_model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    body = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 4096,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    r = requests.post(
        base_url + "/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=180,
    )
    if r.status_code != 200:
        raise Exception(f"LLM API error {r.status_code}: {r.text[:500]}")

    content = r.json()["choices"][0]["message"]["content"].strip()

    if json_mode:
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        return json.loads(content.strip())
    return content


def extract_chunk_facts(chunk_text: str) -> dict:
    """Extract structured facts from one document chunk."""
    try:
        return call_llm(CHUNK_EXTRACTOR_PROMPT, f"DOCUMENT CHUNK:\n{chunk_text}")
    except Exception:
        return {
            "monetary_items": [], "percentages": [], "dates_timelines": [],
            "numeric_claims": [], "deliverables": [], "assumptions": [],
            "compliance_refs": [], "calculations": []
        }


def merge_extractions(chunks: list[dict]) -> dict:
    """Merge extracted data from all chunks."""
    merged = {
        "monetary_items": [],
        "percentages": [],
        "dates_timelines": [],
        "numeric_claims": [],
        "deliverables": [],
        "assumptions": [],
        "compliance_refs": [],
        "calculations": [],
    }
    for chunk in chunks:
        for key in merged:
            items = chunk.get(key, [])
            if isinstance(items, list):
                merged[key].extend(items)

    # Deduplicate simple string lists
    for key in ["deliverables", "assumptions", "compliance_refs"]:
        merged[key] = list(dict.fromkeys(merged[key]))

    return merged


def run_validation(extracted: dict, full_text: str) -> dict:
    """Run the main validation agent."""
    prompt = (
        VALIDATOR_PROMPT
        .replace("{extracted_data}", json.dumps(extracted, indent=2))
        .replace("{doc_text_preview}", full_text[:8000])
    )
    return call_llm("You are AI_Validate, a rigorous proposal review system.", prompt)


# ─── MAIN ENDPOINT ────────────────────────────────────────────────────────────

@app.post("/validate")
async def validate_proposal(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Step 1: Extract text per page
        pages = extract_text_with_pages(file_path)
        if not pages:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

        full_text = " ".join(p["text"] for p in pages)

        # Step 2: Chunk and extract facts in passes
        chunks = chunk_pages(pages, chunk_size=4)
        extracted_per_chunk = [extract_chunk_facts(c["text"]) for c in chunks]

        # Step 3: Merge all extracted facts
        merged = merge_extractions(extracted_per_chunk)

        # Step 4: Run the deep validation agent
        validation = run_validation(merged, full_text)

        # Step 5: Enrich response with metadata
        validation["document_name"] = os.path.splitext(file.filename)[0]
        validation["page_count"] = len(pages)
        validation["extracted_facts"] = {
            "monetary_items_found": len(merged["monetary_items"]),
            "calculations_found": len(merged["calculations"]),
            "deliverables_found": len(merged["deliverables"]),
            "dates_found": len(merged["dates_timelines"]),
            "assumptions_found": len(merged["assumptions"]),
        }
        validation["raw_extraction"] = merged

        return validation

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"LLM returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "service": "AI_Validate"}


# ─── SERVE FRONTEND ───────────────────────────────────────────────────────────

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
