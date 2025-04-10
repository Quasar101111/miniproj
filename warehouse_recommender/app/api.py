from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from .price_predictor import WarehousePricePredictor

app = FastAPI(title="Warehouse Recommender API")

# Add CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.0:8000",  # Django development server
        "http://localhost:8000",   # Alternative Django URL
        "http://127.0.0.1:8000",   # Another common Django URL
        "http://0.0.0.0:8000",     # Django on all interfaces
        "http://app.fronty.localhost:5000",  # Frontend service
        "http://frontserver:5000",  # Frontend service internal Docker network
        "http://app.recommender.localhost",  # Traefik hostname
        "http://localhost",         # Local development
        "http://127.0.0.1",        # Local development
        "http://127.0.0.2",        # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class WarehouseRequest(BaseModel):
    area: float
    latitude: float
    longitude: float

class PriceSuggestion(BaseModel):
    optimal_price: float
    price_range: dict
    price_per_sqft: float
    confidence: float

# Initialize the price predictor
predictor = WarehousePricePredictor()
model_path = os.path.join(os.path.dirname(__file__), "models", "price_predictor.joblib")

# Load the trained model
try:
    predictor.load_model(model_path)
    print("Price prediction model loaded successfully")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    print("Please ensure the model is trained and saved before running the API")

@app.get("/")
async def root():
    return {"message": "Welcome to Warehouse Recommender API"}

@app.post("/predict/price", response_model=PriceSuggestion)
async def predict_price(request: WarehouseRequest):
    try:
        # Get price suggestions using the trained model
        suggestions = predictor.get_optimal_price_suggestions(
            request.area,
            request.latitude,
            request.longitude
        )
        
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Use 0.0.0.0 to allow both internal Docker network and external access
    uvicorn.run(app, host="0.0.0.0", port=8001) 