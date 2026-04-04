import os
import json
import requests
import fitz
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn

def _apply_env_file(path: Path, *, override: bool) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        key = k.strip()
        val = v.strip().strip('"').strip("'")
        if override:
            os.environ[key] = val
        else:
            os.environ.setdefault(key, val)


def load_env():
    # Shared backend keys (same as ignisia/backend/.env used by main FastAPI)
    backend_root = Path(__file__).resolve().parent.parent
    _apply_env_file(backend_root / ".env", override=False)
    # Optional overrides for doc_rag only
    _apply_env_file(Path(__file__).with_name(".env"), override=True)
    if "OPENROUTER_API_KEY" not in os.environ and "api_key" in os.environ:
        os.environ.setdefault("OPENROUTER_API_KEY", os.environ["api_key"])

load_env()

app = FastAPI(title="RFP Single-Pass Analyzer")


@app.on_event("startup")
def _check_openrouter_key() -> None:
    if not os.environ.get("OPENROUTER_API_KEY"):
        import logging

        logging.getLogger("uvicorn.error").warning(
            "OPENROUTER_API_KEY is not set. Add it to ignisia/backend/.env or doc_rag/.env, then restart."
        )
UPLOAD_DIR = Path(__file__).parent / "upload"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = """You are an expert AI system for analyzing RFP documents. \
Given an RFP document, perform the following in one pass: \
extract all explicit questions and convert implicit requirements into clear questions, \
then filter and retain only high-value questions related to scope of work, pricing, timeline, compliance, and key capabilities \
while removing repetitive, low-level, or trivial items, limiting the final set to 10-20 questions. \
For each selected question, classify it with category (technical, pricing, compliance, general) \
and intent (capability_check, compliance_check, information_request, strategy). \
Return strictly valid JSON in the format { "rfp_name": "string", "questions": [{ "question": "string", "category": "...", "intent": "..." }] }. \
Do not hallucinate and ensure clarity and relevance."""

def extract_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    text_blocks = []
    for page in doc:
        text_blocks.append(" ".join(page.get_text("text").split()))
    return "\n\n".join(text_blocks)

def ask_llm(rfp_text: str):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    # It's recommended to use a heavily context-capable model such as GPT-4o-mini or Claude 3 Haiku for one-pass full-document reading
    body = {
        "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"RFP Document: {rfp_text}"
            },
        ],
        "response_format": { "type": "json_object" }
    }
    r = requests.post(
        os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(body),
        timeout=180,
    )
    if r.status_code != 200:
        raise Exception(f"OpenRouter API error: {r.text}")
    
    content = r.json()["choices"][0]["message"]["content"].strip()
    
    # Strip markdown code blocks if the LLM adds them by mistake
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
        
    return json.loads(content.strip())

def generate_pricing_payload(rfp_text: str, pricing_questions: list) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    system_prompt = """You are an expert cost estimator.
Based on the provided RFP text and the specific pricing questions, extract the bill of quantities and project details required for a pricing agent.
The required JSON schema is:
{
  "rfp_items": [
    {
      "name": "string (material or task name)",
      "quantity": float,
      "unit": "string (e.g., sqft, pieces, cubic meters)"
    }
  ],
  "region": "string (default to Mumbai if unknown)",
  "state": "string (default to Maharashtra if unknown)",
  "project_type": "string (residential, commercial, government)",
  "area_sqft": float,
  "duration_weeks": int,
  "is_government_project": boolean
}
Return STRICTLY valid JSON. Do not hallucinate items not present in the RFP. If exact quantities are missing, provide a reasonable estimate based on the text.
"""
    body = {
        "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Pricing Questions:\n{json.dumps(pricing_questions, indent=2)}\n\nRFP Document Snippet:\n{rfp_text[:15000]}"
            },
        ],
        "response_format": { "type": "json_object" }
    }
    r = requests.post(
        os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(body),
        timeout=180,
    )
    if r.status_code != 200:
        raise Exception(f"OpenRouter API error in pricing payload generation: {r.text}")
    
    content = r.json()["choices"][0]["message"]["content"].strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
    return json.loads(content.strip())

def call_pricing_agent(payload: dict) -> dict:
    base = os.environ.get("PRICING_AGENT_URL", "http://127.0.0.1:9000").rstrip("/")
    url = f"{base}/api/v1/price_rfp"
    try:
        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "details": f"Failed to call pricing agent at {url}"}

@app.post("/analyze-rfp")
async def analyze_rfp(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        text = extract_text(file_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the provided PDF.")
            
        result = ask_llm(text)
        
        # Ensure rfp_name defaults properly if the LLM output is generic
        if "rfp_name" not in result or result.get("rfp_name") == "string":
            result["rfp_name"] = os.path.splitext(file.filename)[0]
            
        # Extract pricing questions and query the pricing agent
        pricing_questions = [q for q in result.get("questions", []) if q.get("category") == "pricing"]
        
        pricing_payload = None
        pricing_result = None
        if pricing_questions:
            try:
                pricing_payload = generate_pricing_payload(text, pricing_questions)
                pricing_result = call_pricing_agent(pricing_payload)
            except Exception as pe:
                pricing_result = {"error": str(pe)}

        final_output = {
            "analysis": result,
            "pricing_payload": pricing_payload,
            "pricing_result": pricing_result
        }

        # Save to local JSON output
        output_file = UPLOAD_DIR / f"{result['rfp_name']}_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dumps(final_output, indent=2) # intentional no-save to detect if dumps alone used
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2)

        return final_output
    except json.JSONDecodeError as jde:
        raise HTTPException(status_code=500, detail=f"LLM response was not valid JSON. Error: {jde}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)