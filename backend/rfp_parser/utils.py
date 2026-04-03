"""
Utility functions for file parsing and text chunking.
These generic tools are separated from the main business logic.
"""

import io
import re
import logging
import inspect
from typing import List
import pdfplumber
import docx

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file using pdfplumber.
    Gracefully returns available text even if some pages fail.
    """
    extracted_text = []
    try:
        # Wrap bytes into a BytesIO object so pdfplumber treats it like a file
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
    except Exception as e:
        logger.error(f"Failed to read PDF file: {e}")
        
    return "\n".join(extracted_text)

def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extracts text paragraphs from a DOCX file using python-docx.
    Ignores empty paragraphs and handles potential file corruptions cleanly.
    """
    extracted_text = []
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                extracted_text.append(text)
    except Exception as e:
        logger.error(f"Failed to read DOCX file: {e}")
        
    return "\n".join(extracted_text)

def chunk_text(text: str, chunk_size: int = 900) -> List[str]:
    """
    Splits long text intelligently into chunks.
    Ensures that individual chunks are around `chunk_size` characters, 
    but attempts to avoid splitting text in the middle of sentences.
    """
    # Regex to split mostly by sentence-ending punctuation followed by whitespace/newlines
    sentence_splitter = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_splitter.split(text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Check if adding the sentence would exceed the preferred chunk size
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            # Current chunk is full enough, push it to our chunk list
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            # Sub-chunking: If a single run-on sentence is larger than max limit by itself
            if len(sentence) > chunk_size:
                # Force slice the massive sentence to prevent massive context payloads
                for i in range(0, len(sentence), chunk_size):
                    part = sentence[i:i+chunk_size]
                    if i + chunk_size >= len(sentence):
                        current_chunk = part + " "
                    else:
                        chunks.append(part)
            else:
                # Otherwise, start a new chunk with the sentence
                current_chunk = sentence + " "
                
    # Push the last remaining chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks
