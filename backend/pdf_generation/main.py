from io import BytesIO
from typing import Any

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from node_pdf_bridge import render_pdf_via_node
from rag_service import answer_question
from rfp_pdf_mapper import build_proposal_request_from_rfp_ai
from schemas import ProposalRequest, RagQueryRequest, RagQueryResponse, sample_proposal


app = FastAPI(
    title="Ignisia Proposal PDF API",
    version="1.0.0",
    description="Generate polished proposal response PDFs from structured JSON.",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/proposals/example", response_model=ProposalRequest)
def get_example_proposal() -> ProposalRequest:
    return sample_proposal()


class RfpCombinedPdfBody(BaseModel):
    ai_proposal: dict[str, Any]
    ai_reason: dict[str, Any]


@app.post("/api/proposals/pdf-from-rfp")
def generate_rfp_combined_pdf(body: RfpCombinedPdfBody) -> StreamingResponse:
    """Build a proposal PDF from last RFP analyze JSON + AI strategy JSON."""
    try:
        payload = build_proposal_request_from_rfp_ai(body.ai_proposal, body.ai_reason)
        pdf_bytes = render_pdf_via_node(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}") from exc

    filename = payload.document.file_name or "rfp-response.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@app.post("/api/proposals/pdf")
def generate_proposal_pdf(payload: ProposalRequest) -> StreamingResponse:
    try:
        pdf_bytes = render_pdf_via_node(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}") from exc

    filename = payload.document.file_name or "proposal-response.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@app.post("/api/rag/ask", response_model=RagQueryResponse)
def ask_proposal_question(payload: RagQueryRequest) -> RagQueryResponse:
    try:
        return RagQueryResponse(**answer_question(payload.question))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG request failed: {exc}") from exc
