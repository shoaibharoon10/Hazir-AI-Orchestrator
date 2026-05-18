import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.orchestrate.matching import router as matching_router

app = FastAPI()
app.include_router(matching_router)

client = TestClient(app)

def test_match_and_rank_success():
    """
    Acceptance Scenario 1: Successfully ranks matching providers.
    Sends a payload for an existing service category and asserts deterministic sorting.
    """
    payload = {
        "service_category": "AC Technician",
        "location_context": "Clifton block 9",
        "time_preference": "today 5 PM",
        "urgency_level": "normal"
    }
    response = client.post("/api/orchestrate/match", json=payload)
    assert response.status_code == 200
    
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["error"] is None
    assert len(json_data["data"]) > 0
    
    # Assert deterministic descending sort
    data = json_data["data"]
    if len(data) > 1:
        for i in range(len(data) - 1):
            assert data[i]["composite_score"] >= data[i+1]["composite_score"]
            
    assert "id" in data[0]
    assert "composite_score" in data[0]
    assert "distance_km" in data[0]

def test_match_no_providers_fallback():
    """
    Acceptance Scenario 2: Returns 0-match fallback gracefully without 500 error.
    Sends a payload with an unmatched service category.
    """
    payload = {
        "service_category": "NonExistentService",
        "location_context": "Remote Area",
        "time_preference": "3:00 AM",
        "urgency_level": "urgent"
    }
    response = client.post("/api/orchestrate/match", json=payload)
    
    # Assert successful standard response but with empty data array and warning message
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 0
    assert "No available providers" in json_data["error"]
