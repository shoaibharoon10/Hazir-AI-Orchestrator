# pyrefly: ignore [missing-import]
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.orchestrate.pricing import router as pricing_router

app = FastAPI()
app.include_router(pricing_router)

client = TestClient(app)

def test_calculate_price_success():
    """
    Acceptance Scenario: Valid pricing payload (Intermediate tier, 12km, loyalty silver).
    Base (Intermediate): 1800.00
    Distance Buffer: (12 - 5) = 7km * 25.00 = 175.00
    Surge: 0.00
    Discount (Silver): 50.00
    Net Total: 1800 + 175 - 50 = 1925.00
    """
    payload = {
        "job_category": "Wiring Repair",
        "complexity_tier": "intermediate",
        "distance_km": 12.0,
        "urgency_flag": False,
        "loyalty_tier": "silver"
    }
    
    response = client.post("/api/orchestrate/price", json=payload)
    assert response.status_code == 200
    
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["error"] is None
    
    data = json_data["data"]
    assert data["base_price"] == 1800.00
    assert data["distance_buffer"] == 175.00
    assert data["surge_cost"] == 0.00
    assert data["discount"] == 50.00
    assert data["net_total"] == 1925.00

def test_pricing_edge_cases():
    """
    Acceptance Scenario: Zero-distance, urgent surge, no loyalty.
    Base (Complex): 3000.00
    Distance Buffer: 4.0km (<= 5km baseline) = 0.00
    Surge: 3000 * 0.20 = 600.00 (under 50% cap of 1500)
    Discount: 0.00
    Net Total: 3000 + 0 + 600 - 0 = 3600.00
    """
    payload = {
        "job_category": "AC Installation",
        "complexity_tier": "complex",
        "distance_km": 4.0,
        "urgency_flag": True,
        "loyalty_tier": None
    }
    
    response = client.post("/api/orchestrate/price", json=payload)
    assert response.status_code == 200
    
    json_data = response.json()
    assert json_data["success"] is True
    
    data = json_data["data"]
    assert data["base_price"] == 3000.00
    assert data["distance_buffer"] == 0.00
    assert data["surge_cost"] == 600.00
    assert data["discount"] == 0.00
    assert data["net_total"] == 3600.00
