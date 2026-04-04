from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging

from orchestrator import run_pricing_agent

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(
    title="RFP Pricing Agent API",
    description="API for the parallel MCP construction pricing agent.",
    version="1.0.0",
)

class RFPItem(BaseModel):
    name: str
    quantity: float
    unit: str

class PricingRequest(BaseModel):
    rfp_items: List[RFPItem]
    region: str = "Mumbai"
    state: str = "Maharashtra"
    project_type: str = "commercial"
    area_sqft: float = 1000.0
    duration_weeks: int = 8
    is_government_project: bool = False

@app.post("/api/v1/price_rfp", response_model=Dict[str, Any])
async def price_rfp_endpoint(request: PricingRequest):
    """
    Generate a full cost breakdown based on given RFP items and project details.
    This routes the request to 4 parallel MCP servers to calculate costs.
    """
    logger.info(f"Received pricing request for {len(request.rfp_items)} items. Region: {request.region}")
    
    # Convert Pydantic models to lists of dictionaries as expected by run_pricing_agent
    rfp_items_dict = [item.model_dump() for item in request.rfp_items]
    
    try:
        result = await run_pricing_agent(
            rfp_items=rfp_items_dict,
            region=request.region,
            state=request.state,
            project_type=request.project_type,
            area_sqft=request.area_sqft,
            duration_weeks=request.duration_weeks,
            is_government_project=request.is_government_project,
        )
        return result
    except Exception as e:
        logger.error(f"Error during pricing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=9000, reload=True)
