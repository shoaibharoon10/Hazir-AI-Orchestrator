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

def mock_gemini_unsupported(query: str) -> APIResponseSchema:
    return APIResponseSchema(
        success=True,
        data=IntentExtractionSchema(
            service_category=None,
            location_context="unknown",
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
    data = json_data["data"]
    assert data["status"] == "success"
    # 1. Intent Extraction Verification
    assert data["parsed_intent"]["service_category"] == "AC Technician"
    
    # 2. Provider Matching Verification
    assert data["assigned_provider"]["id"].startswith("PRO-")
    
    # 3. Pricing Breakdown Verification
    assert data["price_breakdown"]["base_price"] > 0
    
    # 4. FSM Booking Verification
    assert data["booking_summary"]["current_status"] == "confirmed"
    assert data["booking_summary"]["booking_id"].startswith("BKG-")
    
    # 5. Agent Trace & Lifecycle Validation
    assert len(data["agent_trace"]) > 0
    assert data["follow_up_schedule"] is not None
    assert len(data["follow_up_schedule"]) == 3
    assert "PlannerAgent" in [t["agent"] for t in data["agent_trace"]]

@patch("src.services.unified_service.GeminiIntentParser.parse_raw_query", side_effect=mock_gemini_unsupported)
def test_unified_orchestration_unsupported_service(mock_parser):
    """
    Acceptance Scenario: Tests that unsupported/unrecognised categories return status='unsupported' with HTTP 200.
    """
    payload = {
        "query": "mujhe aik ninja chahye jo chat repair kare",
        "customer_id": "CUST-U2",
        "user_location": "DHA"
    }
    
    response = client.post("/api/orchestrate/run-all", json=payload)
    
    # Expecting HTTP 200 with status 'unsupported' (never 400/500)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "unsupported"
    assert "AC Technician" in json_data["message"]
    
    agent_trace = json_data["agent_trace"]
    assert len(agent_trace) > 0
    assert any(t["agent"] == "PlannerAgent" for t in agent_trace)
