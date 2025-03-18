import pytest
import numpy as np
from datetime import datetime
from app.schemas import WarehouseBase, TenantBase
from app.advanced_recommender import ContentBasedFilter, CollaborativeFilter, HybridRecommender

# Sample data
@pytest.fixture
def sample_warehouses():
    return [
        WarehouseBase(
            id=1,
            length=100.0,
            width=50.0,
            height=10.0,
            latitude=40.7128,
            longitude=-74.0060,
            rental_price=5000.0,
            facilities=["climate-control", "loading-dock", "security"],
            year_built=datetime(2015, 1, 1)
        ),
        WarehouseBase(
            id=2,
            length=150.0,
            width=75.0,
            height=12.0,
            latitude=40.7135,
            longitude=-74.0070,
            rental_price=7000.0,
            facilities=["climate-control", "security", "forklift"],
            year_built=datetime(2018, 1, 1)
        ),
        WarehouseBase(
            id=3,
            length=80.0,
            width=40.0,
            height=8.0,
            latitude=40.7500,
            longitude=-74.1000,
            rental_price=3000.0,
            facilities=["loading-dock"],
            year_built=datetime(2010, 1, 1)
        )
    ]

@pytest.fixture
def sample_tenant():
    return TenantBase(
        id=101,
        latitude=40.7200,
        longitude=-74.0100,
        preferred_price_range=(4000.0, 6000.0),
        lease_history_count=2
    )

def test_content_based_filter(sample_warehouses, sample_tenant):
    # Initialize content-based filter
    content_filter = ContentBasedFilter()
    
    # Get recommendations
    scores = content_filter.recommend(sample_warehouses, sample_tenant)
    
    # Assert expected behavior
    assert len(scores) == len(sample_warehouses)
    assert all(0 <= score <= 1 for score in scores)
    
    # First warehouse should have highest score as it's closest to tenant preferences
    assert scores[0] > scores[2]

def test_collaborative_filter():
    # Initialize collaborative filter
    collab_filter = CollaborativeFilter()
    
    # Add some interaction data
    collab_filter.add_tenant_warehouse_interaction(101, 1)
    collab_filter.add_tenant_warehouse_interaction(101, 2)
    collab_filter.add_tenant_warehouse_interaction(102, 1)
    collab_filter.add_tenant_warehouse_interaction(102, 3)
    collab_filter.add_tenant_warehouse_interaction(103, 2)
    
    # Find similar tenants
    similar_tenants = collab_filter.find_similar_tenants(101)
    
    # Check that we found similar tenants
    assert len(similar_tenants) > 0
    # Either tenant 102 or 103 should be in the results (both have overlap with 101)
    tenant_ids = [tenant_id for tenant_id, _ in similar_tenants]
    assert 102 in tenant_ids or 103 in tenant_ids

def test_hybrid_recommender(sample_warehouses, sample_tenant):
    # Initialize hybrid recommender
    hybrid = HybridRecommender()
    
    # Add some interaction data
    hybrid.add_interaction(101, 1)
    hybrid.add_interaction(101, 2)
    hybrid.add_interaction(102, 1)
    hybrid.add_interaction(102, 3)
    
    # Get recommendations (content-based only)
    content_scores = hybrid.recommend(sample_warehouses, sample_tenant)
    assert len(content_scores) == len(sample_warehouses)
    
    # Get recommendations (hybrid)
    hybrid_scores = hybrid.recommend(sample_warehouses, sample_tenant, tenant_id=101)
    assert len(hybrid_scores) == len(sample_warehouses)
    
    # Check all scores are valid
    assert all(0 <= score <= 1 for score in hybrid_scores) 