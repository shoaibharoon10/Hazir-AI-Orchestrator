import pytest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.orchestrate.unified import router as unified_router
from src.schemas.intent import APIResponseSchema, IntentExtractionSchema

app = FastAPI()
app.include_router(unified_router)

client = TestClient(app)

def mock_gemini_success(query: str) -> APIResponseSchema:
    return APIResponseSchema(
        success=True,
        data=IntentExtractionSchema(
            service_category="AC Technician",
            location_context="Clifton Block 9",
            time_preference="2026-05-20T10:00:00Z",
            urgency_level="urgent",
            confidence_score=0.95
        )
    )

def mock_gemini_0_match(query: str) -> APIResponseSchema:
    return APIResponseSchema(
        success=True,
        data=IntentExtractionSchema(
            service_category="Plumber",
            location_context="Nowhere",
            time_preference="2026-05-20T10:00:00Z",
            urgency_level="normal",
            confidence_score=0.95
        )
    )

@patch("src.services.unified_service.GeminiIntentParser.parse_raw_query", side_effect=mock_gemini_success)
def test_unified_orchestration_flow_success(mock_parser):
    """
    Acceptance Scenario: Tests successful raw text query to confirmed booking flow natively.
    """
    payload = {
        "query": "mujhe ac theek karwana hai Clifton me",
        "customer_id": "CUST-U1",
        "user_location": "Clifton Block 9"
    }
    
    response = client.post("/api/orchestrate/run-all", json=payload)
    assert response.status_code == 200
    
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["error"] is None
    
    data = json_data["data"]
    
    # 1. Intent Extraction Verification
    assert data["parsed_intent"]["service_category"] == "AC Technician"
    
    # 2. Provider Matching Verification
    assert data["assigned_provider"]["id"] == "prov_ac_1"
    
    # 3. Pricing Breakdown Verification
    assert data["price_breakdown"]["base_price"] > 0
    
    # 4. FSM Booking Verification
    assert data["booking_summary"]["current_status"] == "confirmed"
    assert data["booking_summary"]["booking_id"].startswith("BKG-")

@patch("src.services.unified_service.GeminiIntentParser.parse_raw_query", side_effect=mock_gemini_0_match)
def test_unified_orchestration_rollback_failure(mock_parser):
    """
    Acceptance Scenario: Tests graceful downstream aborts for a 0-match (category unknown).
    """
    payload = {
        "query": "mujhe aik ninja chahye jo chat repair kare",
        "customer_id": "CUST-U2",
        "user_location": "DHA"
    }
    
    response = client.post("/api/orchestrate/run-all", json=payload)
    
    # Expecting 400 Bad Request caught by OrchestrationError, not 500
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["success"] is False
    assert "Pipeline transaction aborted" in json_data["error"]
    
    error_data = json_data["data"]
    assert error_data["error_stage"] == "matching"
    assert "No providers found" in error_data["message"]
