import os
import json
import requests
import fitz
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn

def load_env():
    env = Path(__file__).with_name(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    if "OPENROUTER_API_KEY" not in os.environ and "api_key" in os.environ:
        os.environ["OPENROUTER_API_KEY"] = os.environ["api_key"]

load_env()

app = FastAPI(title="RFP Single-Pass Analyzer")
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
            
        return result
    except json.JSONDecodeError as jde:
        raise HTTPException(status_code=500, detail=f"LLM response was not valid JSON. Error: {jde}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)