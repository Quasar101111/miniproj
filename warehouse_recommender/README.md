# Warehouse Recommender System

Advanced recommendation system for warehouse-tenant matching using multiple recommendation algorithms.

## Features

- **Neural Network Recommender**: Original recommendation engine based on a neural network model
- **Content-Based Filtering**: Recommends warehouses based on tenant preferences and warehouse characteristics
- **Collaborative Filtering**: Recommends warehouses based on tenant-warehouse interaction history
- **Hybrid Approach**: Combines both content-based and collaborative filtering for better recommendations

## Components

### Content-Based Filtering

Content-based filtering recommends warehouses by matching warehouse characteristics with tenant preferences:

- Location proximity (using coordinates)
- Price matching (tenant price range vs. warehouse rental price)
- Facility similarity (using TF-IDF and cosine similarity)

### Collaborative Filtering

Collaborative filtering recommends warehouses based on historical tenant-warehouse interactions:

- Finds similar tenants based on Jaccard similarity
- Recommends warehouses liked by similar tenants
- Considers tenant leasing history

### Hybrid Approach

The hybrid approach combines the strengths of both methods:

- Uses content-based filtering for new tenants with no history
- Enhances recommendations with collaborative data when available
- Offers weighted combination of both approaches

## API Endpoints

### Get Recommendations

```
POST /recommend/
```

Query parameters:
- `algorithm`: Choose between 'neural', 'content', 'collaborative', or 'hybrid'
- `tenant_id`: Required for collaborative and hybrid approaches
- `limit`: Maximum number of recommendations to return (default: 5)

### Record Interaction

```
POST /record-interaction/
```

Parameters:
- `tenant_id`: ID of the tenant
- `warehouse_id`: ID of the warehouse

This endpoint records interactions to improve future collaborative recommendations.

## Installation and Usage

1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `uvicorn app.main:app --reload`
3. API documentation available at: http://localhost:8000/docs 