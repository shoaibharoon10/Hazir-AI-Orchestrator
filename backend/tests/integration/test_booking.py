import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.orchestrate.booking import router as booking_router

app = FastAPI()
app.include_router(booking_router)

client = TestClient(app)

def test_booking_lifecycle_success():
    """
    Acceptance Scenario: Tests standard booking confirmation returning a valid ID and state.
    """
    payload = {
        "provider_id": "PRV-TEST-100",
        "job_category": "Electrician",
        "scheduled_time": "2026-05-20T10:00:00Z",
        "dynamic_price": 1925.00,
        "customer_id": "CUST-123",
        "location_context": "Clifton Block 9"
    }
    
    response = client.post("/api/orchestrate/book", json=payload)
    assert response.status_code == 200
    
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["error"] is None
    
    data = json_data["data"]
    assert "booking_id" in data
    assert data["booking_id"].startswith("BKG-")
    assert data["provider_id"] == "PRV-TEST-100"
    assert data["current_status"] == "confirmed"
    assert data["net_price"] == 1925.00

def test_double_booking_prevention():
    """
    Acceptance Scenario: Tests deterministic double-booking rejection matrix.
    Sends an initial booking, then attempts an identical request to trigger error state.
    """
    payload = {
        "provider_id": "PRV-TEST-200",
        "job_category": "Plumber",
        "scheduled_time": "2026-05-21T14:30:00Z",
        "dynamic_price": 1500.00,
        "customer_id": "CUST-456",
        "location_context": "DHA Phase 5"
    }
    
    # 1. First booking should succeed
    response_1 = client.post("/api/orchestrate/book", json=payload)
    assert response_1.status_code == 200
    assert response_1.json()["success"] is True
    
    # 2. Second booking with exact same provider and time should fail gracefully
    response_2 = client.post("/api/orchestrate/book", json=payload)
    assert response_2.status_code == 400
    
    json_data = response_2.json()
    assert json_data["success"] is False
    assert json_data["error"] is not None
    assert "already booked" in json_data["error"].lower()
