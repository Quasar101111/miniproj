#!/usr/bin/env python
"""
Demonstration script for warehouse recommendation system.
This script shows how to use the different recommendation algorithms directly.
"""

import numpy as np
from datetime import datetime
from app.schemas import WarehouseBase, TenantBase
from app.advanced_recommender import ContentBasedFilter, CollaborativeFilter, HybridRecommender
from app.recommender import WarehouseRecommender

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def main():
    # Create sample data
    warehouses = [
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
        ),
        WarehouseBase(
            id=4,
            length=200.0,
            width=100.0,
            height=15.0,
            latitude=41.0000,
            longitude=-74.5000,
            rental_price=10000.0,
            facilities=["climate-control", "loading-dock", "security", "forklift", "office-space"],
            year_built=datetime(2020, 1, 1)
        ),
        WarehouseBase(
            id=5,
            length=60.0,
            width=30.0,
            height=6.0,
            latitude=40.7300,
            longitude=-74.0200,
            rental_price=2000.0,
            facilities=[],
            year_built=datetime(2005, 1, 1)
        )
    ]
    
    tenant = TenantBase(
        id=101,
        latitude=40.7200,
        longitude=-74.0100,
        preferred_price_range=(4000.0, 6000.0),
        lease_history_count=2
    )
    
    # 1. Neural Network Recommender
    print_separator("Neural Network Recommender")
    nn_recommender = WarehouseRecommender()
    nn_scores = nn_recommender.predict(warehouses, tenant)
    print_recommendations(warehouses, nn_scores, "Neural Network")
    
    # 2. Content-Based Filtering
    print_separator("Content-Based Filtering")
    content_filter = ContentBasedFilter()
    content_scores = content_filter.recommend(warehouses, tenant)
    print_recommendations(warehouses, content_scores, "Content-Based")
    
    # 3. Collaborative Filtering
    print_separator("Collaborative Filtering")
    collab_filter = CollaborativeFilter()
    
    # Add interaction data
    print("Adding interaction data...")
    tenant_ids = [101, 102, 103, 104]
    
    # Tenant 101 likes warehouses 1 and 2
    collab_filter.add_tenant_warehouse_interaction(101, 1)
    collab_filter.add_tenant_warehouse_interaction(101, 2)
    
    # Tenant 102 likes warehouses 1 and 3
    collab_filter.add_tenant_warehouse_interaction(102, 1)
    collab_filter.add_tenant_warehouse_interaction(102, 3)
    
    # Tenant 103 likes warehouses 2 and 4
    collab_filter.add_tenant_warehouse_interaction(103, 2)
    collab_filter.add_tenant_warehouse_interaction(103, 4)
    
    # Tenant 104 likes warehouses 3 and 5
    collab_filter.add_tenant_warehouse_interaction(104, 3)
    collab_filter.add_tenant_warehouse_interaction(104, 5)
    
    # Find similar tenants to tenant 101
    similar_tenants = collab_filter.find_similar_tenants(101)
    print("\nTenants similar to tenant 101:")
    for tenant_id, similarity in similar_tenants:
        print(f"  Tenant {tenant_id}: similarity = {similarity:.2f}")
    
    # Get recommendations for tenant 101
    collab_scores = collab_filter.recommend(101, warehouses)
    print_recommendations(warehouses, collab_scores, "Collaborative")
    
    # 4. Hybrid Recommender
    print_separator("Hybrid Recommender")
    hybrid = HybridRecommender()
    
    # Copy interaction data from the collaborative filter
    for tenant_id in tenant_ids:
        for warehouse_id in collab_filter.tenant_history.get(tenant_id, []):
            hybrid.add_interaction(tenant_id, warehouse_id)
    
    # Get hybrid recommendations
    hybrid_scores = hybrid.recommend(warehouses, tenant, tenant_id=101)
    print_recommendations(warehouses, hybrid_scores, "Hybrid")
    
    # Compare all methods
    print_separator("Comparison of All Methods")
    compare_methods(warehouses, nn_scores, content_scores, collab_scores, hybrid_scores)

def print_recommendations(warehouses, scores, method_name):
    """Print recommendations with scores."""
    warehouse_scores = list(zip(warehouses, scores))
    warehouse_scores.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{method_name} Recommendations:")
    for i, (warehouse, score) in enumerate(warehouse_scores):
        print(f"  Rank {i+1}: Warehouse {warehouse.id} - Score: {score:.4f}")
        print(f"    Location: ({warehouse.latitude:.4f}, {warehouse.longitude:.4f})")
        print(f"    Size: {warehouse.length}x{warehouse.width}x{warehouse.height}")
        print(f"    Price: ${warehouse.rental_price:.2f}")
        print(f"    Facilities: {', '.join(warehouse.facilities) if warehouse.facilities else 'None'}")
        print(f"    Year built: {warehouse.year_built.year}")
        print()

def compare_methods(warehouses, nn_scores, content_scores, collab_scores, hybrid_scores):
    """Compare rankings from different recommendation methods."""
    methods = {
        "Neural Network": nn_scores,
        "Content-Based": content_scores,
        "Collaborative": collab_scores,
        "Hybrid": hybrid_scores
    }
    
    # Create a table with warehouse IDs and their ranking in each method
    print("Warehouse Rankings by Method:")
    print(f"{'Warehouse ID':<12} | {'Neural Net':<10} | {'Content':<10} | {'Collab':<10} | {'Hybrid':<10}")
    print("-" * 60)
    
    for warehouse in warehouses:
        rankings = {}
        for method_name, scores in methods.items():
            # Get ranking (1-indexed) of this warehouse
            ranking = list(np.argsort(-scores)).index(warehouse.id - 1) + 1
            rankings[method_name] = ranking
        
        print(f"{warehouse.id:<12} | {rankings['Neural Network']:<10} | {rankings['Content-Based']:<10} | {rankings['Collaborative']:<10} | {rankings['Hybrid']:<10}")

if __name__ == "__main__":
    main() 