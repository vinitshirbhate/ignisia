"""
Orchestrates the document processing flow via LangGraph.
Integrates file parsing, chunking, LLM API calls via OpenRouter, and deduplication.
"""

import os
import logging
from typing import List, Dict, Any, TypedDict, Annotated
import operator

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END

from prompts import SYSTEM_PROMPT, AnalysisOutput, QuestionData
from utils import extract_text_from_pdf, extract_text_from_docx, chunk_text
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    """LangGraph state representation."""
    filename: str
    file_bytes: bytes
    file_extension: str
    text: str
    chunks: List[str]
    current_chunk_index: int
    extracted_questions: Annotated[List[QuestionData], operator.add]
    unique_questions: List[QuestionData]
    error: str

# -----------------
# LangGraph Nodes
# -----------------

def extract_text_node(state: GraphState):
    """Node: Extract text from uploaded document."""
    logger.info("Graph Node: extract_text")
    ext = state.get("file_extension")
    file_bytes = state.get("file_bytes")
    
    if ext == "pdf":
        text = extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        text = extract_text_from_docx(file_bytes)
    else:
        text = ""
        
    if not text.strip():
        return {"error": "Could not extract readable text."}
    return {"text": text}

def chunk_text_node(state: GraphState):
    """Node: Split the document text into chunks."""
    logger.info("Graph Node: chunk_text")
    text = state.get("text", "")
    chunks = chunk_text(text, chunk_size=900)
    return {"chunks": chunks, "current_chunk_index": 0}

def llm_extraction_node(state: GraphState):
    """Node: Make LLM call for a specific chunk via OpenRouter."""
    index = state.get("current_chunk_index", 0)
    chunks = state.get("chunks", [])
    
    logger.info(f"Graph Node: llm_extraction (Chunk {index + 1}/{len(chunks)})")
    chunk = chunks[index]
    
    # Initialize OpenRouter ChatOpenAI provider abstraction via LangChain
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", # Can configure valid openrouter model string
        api_key=os.environ.get("OPENROUTER_API_KEY", "dummy"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.0,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    # Since the new SYSTEM_PROMPT contains the `{text}` tag natively as a full template
    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
    
    chain = prompt | llm | JsonOutputParser()
    
    extracted_qs = []
    if chunk.strip():
        try:
            result = chain.invoke({"text": chunk})
            
            if "questions" in result:
                for q_dict in result["questions"]:
                    try:
                        extracted_qs.append(QuestionData(**q_dict))
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Error processing chunk {index}: {e}")
            
    # Return extracted items (will be appended via operator.add) and increment index
    return {"extracted_questions": extracted_qs, "current_chunk_index": index + 1}

def deduplication_node(state: GraphState):
    """Node: Deduplicate extracted items across all chunks."""
    logger.info("Graph Node: deduplication")
    questions = state.get("extracted_questions", [])
    
    # Deduplicate questions by question text
    seen_qs = set()
    unique_qs = []
    for q in questions:
        norm_text = q.question_text.strip().lower()
        if norm_text not in seen_qs:
            seen_qs.add(norm_text)
            unique_qs.append(q)
            
    return {"unique_questions": unique_qs}


# -----------------
# LangGraph Routing
# -----------------

def route_after_extract(state: GraphState):
    if state.get("error"):
        return END
    if not state.get("text"):
        return END
    return "chunk_text"

def check_more_chunks(state: GraphState):
    index = state.get("current_chunk_index", 0)
    chunks = state.get("chunks", [])
    if index < len(chunks):
        return "llm_extraction"
    return "deduplication"


# -----------------
# Graph Compilation
# -----------------

builder = StateGraph(GraphState)
builder.add_node("extract_text", extract_text_node)
builder.add_node("chunk_text", chunk_text_node)
builder.add_node("llm_extraction", llm_extraction_node)
builder.add_node("deduplication", deduplication_node)

builder.set_entry_point("extract_text")

# Edges
builder.add_conditional_edges("extract_text", route_after_extract, {"chunk_text": "chunk_text", END: END})
builder.add_edge("chunk_text", "llm_extraction")

# Cyclic loop through chunks until exhausted, then jump to deduplication
builder.add_conditional_edges("llm_extraction", check_more_chunks, {"llm_extraction": "llm_extraction", "deduplication": "deduplication"})
builder.add_edge("deduplication", END)

# Compile into a runnable
graph = builder.compile()


def process_rfp_document(filename: str, file_bytes: bytes, file_extension: str) -> Dict[str, Any]:
    """External hook to kick off LangGraph execution."""
    initial_state = {
        "filename": filename,
        "file_bytes": file_bytes,
        "file_extension": file_extension,
        "text": "",
        "chunks": [],
        "current_chunk_index": 0,
        "extracted_questions": [],
        "unique_questions": [],
        "error": ""
    }
    
    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"Graph execution failed: {e}")
        return {
            "rfp_name": os.path.splitext(filename)[0],
            "questions": [],
            "error": str(e)
        }
        
    if final_state.get("error"):
        return {
            "rfp_name": os.path.splitext(filename)[0],
            "questions": [],
            "error": final_state["error"]
        }
        
    unique_qs = final_state.get("unique_questions", [])
    
    return {
        "rfp_name": os.path.splitext(filename)[0],
        "questions": [q.model_dump() for q in unique_qs]
    }
