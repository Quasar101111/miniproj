# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_recommendations():
    test_data = {
        "tenant": {
            "id": 1,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "lease_history_count": 2,
            "preferred_price_range": [5000, 10000]
        },
        "available_warehouses": [
            {
                "id": 1,
                "length": 100.0,
                "width": 50.0,
                "height": 10.0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "rental_price": 5000.0,
                "facilities": ["loading_dock", "security"],
                "year_built": 2020
            }
        ]
    }
    
    response = client.post("/recommend/", json=test_data)
    assert response.status_code == 200
    assert isinstance(response.json(), list)