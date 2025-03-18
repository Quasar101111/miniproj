# app/main.py
from fastapi import FastAPI, HTTPException, Query, Depends
from .schemas import RecommendationRequest, RecommendationResponse
from .recommender import WarehouseRecommender
from .advanced_recommender import HybridRecommender, ContentBasedFilter, CollaborativeFilter
from datetime import datetime
from typing import List, Optional, Dict

app = FastAPI(
    title="Warehouse Recommender API",
    description="API for warehouse recommendations using machine learning",
    version="1.0.0"
)

# Initialize recommenders
recommender = WarehouseRecommender()
hybrid_recommender = HybridRecommender()

@app.get("/")
async def root():
    return {"message": "Welcome to Warehouse Recommender API"}

@app.post("/recommend/", response_model=List[RecommendationResponse])
async def get_recommendations(
    request: RecommendationRequest,
    limit: int = Query(5, ge=1, le=20),  # Limit with validation
    algorithm: str = Query("hybrid", description="Recommendation algorithm to use: 'neural', 'content', 'collaborative', or 'hybrid'"),
    tenant_id: Optional[int] = Query(None, description="Tenant ID for collaborative filtering (required for collaborative and hybrid algorithms)")
):
    if not request.available_warehouses:
        return []
        
    try:
        scores = None
        
        # Choose algorithm based on query parameter
        if algorithm == "neural":
            # Use the original neural network recommender
            scores = recommender.predict(
                request.available_warehouses,
                request.tenant
            )
        elif algorithm == "content":
            # Use content-based filtering
            content_filter = hybrid_recommender.content_based
            scores = content_filter.recommend(
                request.available_warehouses,
                request.tenant
            )
        elif algorithm == "collaborative":
            # Use collaborative filtering (requires tenant_id)
            if tenant_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="tenant_id is required for collaborative filtering"
                )
            
            collab_filter = hybrid_recommender.collaborative
            scores = collab_filter.recommend(
                tenant_id,
                request.available_warehouses
            )
        elif algorithm == "hybrid":
            # Use hybrid approach (requires tenant_id)
            if tenant_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="tenant_id is required for hybrid recommendations"
                )
                
            scores = hybrid_recommender.recommend(
                request.available_warehouses,
                request.tenant,
                tenant_id
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown algorithm: {algorithm}. Use 'neural', 'content', 'collaborative', or 'hybrid'"
            )
        
        if len(scores) == 0:
            return []
       
        # Sort warehouses by scores
        warehouse_scores = list(zip(
            request.available_warehouses,
            scores
        ))
        warehouse_scores.sort(key=lambda x: x[1], reverse=True)
       
        # Prepare response
        recommendations = [
            RecommendationResponse(
                warehouse_id=w.id,
                similarity_score=float(score),
                ranking=idx + 1,
                recommended_at=datetime.now()
            )
            for idx, (w, score) in enumerate(warehouse_scores[:limit])
        ]
       
        return recommendations
   
    except Exception as e:
        # Log the error but return a more generic message
        print(f"Error in recommendation: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while generating recommendations"
        )

@app.post("/record-interaction/")
async def record_interaction(
    tenant_id: int,
    warehouse_id: int
):
    """Record tenant-warehouse interaction to improve future collaborative recommendations"""
    try:
        hybrid_recommender.add_interaction(tenant_id, warehouse_id)
        return {"status": "success", "message": "Interaction recorded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record interaction: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "model_ready": recommender is not None and hybrid_recommender is not None
    }