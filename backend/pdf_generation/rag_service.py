import json
import os
from functools import lru_cache
from pathlib import Path

import fitz
import numpy as np
import requests
from sentence_transformers import SentenceTransformer


RAG_DIR = Path(__file__).resolve().parent.parent.parent / "RAG"
PDF_PATH = RAG_DIR / "proposal.pdf"
ENV_PATH = RAG_DIR / ".env"


def _load_env() -> None:
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    if "OPENROUTER_API_KEY" not in os.environ and "api_key" in os.environ:
        os.environ["OPENROUTER_API_KEY"] = os.environ["api_key"]


def _chunk_words(words: list[str], size: int = 300, overlap: int = 50) -> list[str]:
    step = max(1, size - overlap)
    return [" ".join(words[i : i + size]) for i in range(0, len(words), step) if words[i : i + size]]


def _extract_chunks(pdf_path: Path) -> list[dict[str, str | int]]:
    doc = fitz.open(pdf_path)
    chunks: list[dict[str, str | int]] = []
    for page_no, page in enumerate(doc, 1):
        text = " ".join(page.get_text("text").split())
        for chunk in _chunk_words(text.split()):
            chunks.append({"page": page_no, "text": chunk})
    return chunks


@lru_cache(maxsize=1)
def _embedder() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def _index() -> tuple[list[dict[str, str | int]], np.ndarray]:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")
    chunks = _extract_chunks(PDF_PATH)
    if not chunks:
        raise ValueError("No text extracted from PDF.")
    embeddings = _embedder().encode(
        [str(chunk["text"]) for chunk in chunks],
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")
    return chunks, embeddings


def _retrieve(question: str, k: int = 3) -> list[dict[str, str | int]]:
    chunks, embeddings = _index()
    query = _embedder().encode([question], normalize_embeddings=True, convert_to_numpy=True)[0].astype("float32")
    indices = np.argsort(-(embeddings @ query))[:k]
    return [chunks[int(i)] for i in indices]


def _ask_llm(question: str, hits: list[dict[str, str | int]]) -> str:
    _load_env()
    api_key = os.environ["OPENROUTER_API_KEY"]
    prompt = "\n\n".join(f"[Page {hit['page']}]\n{hit['text']}" for hit in hits)
    body = {
        "model": os.getenv("OPENROUTER_MODEL", "qwen/qwen3-8b"),
        "messages": [
            {
                "role": "system",
                "content": "Answer only from the provided context. Be concise and cite source pages like [p.2]. If unsure, say so.",
            },
            {"role": "user", "content": f"Context:\n{prompt}\n\nQuestion: {question}"},
        ],
    }
    response = requests.post(
        os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        data=json.dumps(body),
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def answer_question(question: str) -> dict:
    hits = _retrieve(question)
    return {
        "answer": _ask_llm(question, hits),
        "pages": sorted({int(hit["page"]) for hit in hits}),
        "sources": [{"page": int(hit["page"]), "excerpt": str(hit["text"])[:280]} for hit in hits],
    }
