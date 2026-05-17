import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.orchestrate.intent import router as intent_router

# Setup a minimal test FastAPI app with our router for integration testing
app = FastAPI()
app.include_router(intent_router)

client = TestClient(app)

def test_acceptance_scenario_1_high_confidence():
    """
    Acceptance Scenario 1: High confidence query parsing.
    Sends a clear, mixed-language query that should result in a successful extraction.
    """
    payload = {
        "query": "mujhe ac theek karwana hai Clifton block 9 me aj sham 5 baje tak, bohot zaruri hai"
    }
    response = client.post("/api/orchestrate/intent", json=payload)
    
    assert response.status_code == 200
    json_data = response.json()
    
    # Assert successful APIResponseSchema wrapping
    assert json_data.get("success") is True
    assert "data" in json_data
    assert json_data.get("error") is None
    
    # Assert inner structured keys from IntentExtractionSchema
    data = json_data["data"]
    assert "service_category" in data
    assert "location_context" in data
    assert "time_preference" in data
    assert "urgency_level" in data
    assert "confidence_score" in data
    
    # Assert confidence threshold
    assert data["confidence_score"] >= 0.70

def test_acceptance_scenario_2_low_confidence():
    """
    Acceptance Scenario 2: Low confidence query parsing.
    Sends a vague query to trigger the low-confidence gate (<0.70).
    """
    payload = {
        "query": "I need help with my lights"
    }
    response = client.post("/api/orchestrate/intent", json=payload)
    
    # Low confidence should trigger HTTP 400 Bad Request
    assert response.status_code == 400
    json_data = response.json()
    
    # Assert error APIResponseSchema wrapping
    assert json_data.get("success") is False
    assert "data" in json_data
    
    # Assert it returns exactly one clarifying question inside the error schema payload
    data = json_data["data"]
    assert "error" in data
    assert "clarifying_question" in data
    assert isinstance(data["clarifying_question"], str)
    assert len(data["clarifying_question"]) > 0
