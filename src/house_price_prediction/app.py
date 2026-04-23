"""
FastAPI backend for House Price Prediction.
Exposes endpoints to predict house prices given an address using free, legal APIs.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .address_to_price import PricePredictionPipeline
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="House Price Prediction API",
    description="Predict house prices from addresses using County Assessor, Census, and Geocoding APIs",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the pipeline once on startup
pipeline = None


@app.on_event("startup")
async def startup_event():
    global pipeline
    pipeline = PricePredictionPipeline()
    logger.info("Pipeline initialized")


class AddressRequest(BaseModel):
    address: str


class PriceResponse(BaseModel):
    address: str
    predicted_price: float
    confidence: float
    error_margin: float
    error_margin_low: float
    error_margin_high: float
    all_15_features: dict
    timestamp: str


@app.get("/")
async def root():
    """API status endpoint."""
    return {
        "status": "running",
        "service": "House Price Prediction API",
        "endpoints": {
            "predict": "/predict",
            "docs": "/docs"
        }
    }


@app.post("/predict", response_model=PriceResponse)
async def predict_price(request: AddressRequest):
    """
    Predict house price from an address.

    Uses free, legal APIs:
    - Nominatim (OpenStreetMap) for geocoding
    - FCC API for Census tract lookup
    - County Assessor for property data
    - Census data for economic indicators

    Args:
        address: Full address (e.g., "123 Main St, Seattle, WA 98101")

    Returns:
        Price prediction with confidence and feature breakdown
    """
    try:
        # Initialize pipeline if needed
        global pipeline
        if pipeline is None:
            pipeline = PricePredictionPipeline()

        if not request.address or len(request.address.strip()) < 5:
            raise HTTPException(status_code=400, detail="Address must be at least 5 characters")

        logger.info(f"Processing prediction for: {request.address}")
        result = pipeline.predict_price(request.address)

        return PriceResponse(
            address=result['address'],
            predicted_price=result['predicted_price'],
            confidence=result['confidence'],
            error_margin=result['error_margin'],
            error_margin_low=result['error_margin_low'],
            error_margin_high=result['error_margin_high'],
            all_15_features=result['all_15_features'],
            timestamp=result['timestamp']
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/batch-predict")
async def batch_predict(addresses: list[AddressRequest]):
    """
    Predict prices for multiple addresses.

    Args:
        addresses: List of address requests

    Returns:
        List of predictions
    """
    results = []
    for req in addresses:
        try:
            result = await predict_price(req)
            results.append(result)
        except HTTPException as e:
            results.append({
                "address": req.address,
                "error": e.detail
            })
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
