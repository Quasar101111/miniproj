from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from datetime import datetime

class WarehouseBase(BaseModel):
    id: int
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    rental_price: float = Field(..., gt=0)
    facilities: List[str] = []
    year_built: datetime  # Changed from int to datetime to match Django model

    class Config:
        from_attributes = True  # This replaces the orm_mode in newer Pydantic versions

class TenantBase(BaseModel):
    id: int
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    preferred_price_range: Optional[Tuple[float, float]] = None
    lease_history_count: int = Field(default=0, ge=0)

    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    tenant: TenantBase
    available_warehouses: List[WarehouseBase]

class RecommendationResponse(BaseModel):
    warehouse_id: int
    similarity_score: float = Field(..., ge=0, le=1)
    ranking: int = Field(..., gt=0)
    recommended_at: Optional[datetime] = None