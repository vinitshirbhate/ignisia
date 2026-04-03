"""
Main FastAPI entry point for the RFP Parser Agent.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, status
import logging
import os
from parser import process_rfp_document
from dotenv import load_dotenv
load_dotenv()

# Setup basic logging for production style
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RFP Parser Agent",
    description="API for parsing RFP documents and extracting structured questions.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Verify essential environment variables on startup."""
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY is missing. Extraction features may fail unless implicitly loaded.")

@app.post("/parse-rfp", response_model=dict, summary="Upload and parse an RFP document")
async def parse_rfp(file: UploadFile = File(...)):
    """
    Accepts an RFP file (PDF or DOCX) via POST.
    Reads its content, extracts textual information, chunks the text, and
    uses LangGraph to derive structural questions, returning JSON.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No filename provided in upload."
        )

    # Determine file extension to validate supported formats
    file_extension = file.filename.lower().split('.')[-1]
    if file_extension not in ['pdf', 'docx']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{file_extension}'. Please upload PDF or DOCX."
        )

    try:
        # Read file contents into memory safely
        file_bytes = await file.read()
        logger.info(f"Successfully read file context. Size: {len(file_bytes)} bytes.")
        
        # Hand off bytes to our robust parsing pipeline
        result = process_rfp_document(
            filename=file.filename,
            file_bytes=file_bytes,
            file_extension=file_extension
        )
        
        return result

    except Exception as e:
        logger.error(f"Unexpected error during RFP processing: {str(e)}", exc_info=True)
        # We don't expose internal errors to the client by default in production
        # but here we return detail for debugging 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    # Local execution guard for testing without an external ASGI runner
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
