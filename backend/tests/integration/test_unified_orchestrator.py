import pytest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.orchestrate.unified import router as unified_router
from src.schemas.intent import APIResponseSchema, IntentExtractionSchema

app = FastAPI()
app.include_router(unified_router)

client = TestClient(app)

# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@patch("src.services.unified_service.GeminiIntentParser.parse_raw_query", side_effect=mock_gemini_success)
def test_unified_orchestration_flow_success(mock_parser):
    """
    Acceptance Scenario: Full pipeline E2E — Intent -> Match -> Price -> Book -> Follow-up.
    Validates the complete multi-agent payload contract.
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

    # 1. Intent Extraction
    assert data["parsed_intent"]["service_category"] == "AC Technician"

    # 2. Multi-Option Provider Matching
    assert data["multi_provider_options"]["best_match"] is not None
    assert data["multi_provider_options"]["best_match"]["provider_id"].startswith("PRO-")
    assert "selection_reasoning" in data["multi_provider_options"]["best_match"]
    assert isinstance(data["multi_provider_options"]["alternatives"], list)

    # 3. Backward-compat single provider reference
    assert data["assigned_provider"]["id"].startswith("PRO-")

    # 4. Pricing — standard breakdown + itemised receipt
    assert data["price_breakdown"]["base_price"] > 0
    assert data["dynamic_receipt"]["grand_total"] > 0
    assert data["dynamic_receipt"]["base_fee"] > 0

    # 5. Booking FSM
    assert data["booking_summary"]["current_status"] == "confirmed"
    assert data["booking_summary"]["booking_id"].startswith("BKG-")

    # 6. Bilingual SMS confirmation
    assert data["client_confirmation_sms"] is not None
    assert "Booking Confirmed" in data["client_confirmation_sms"]
    assert "PKR" in data["client_confirmation_sms"]

    # 7. Agent Trace — all 5 agents must appear
    trace_agents = [t["agent"] for t in data["agent_trace"]]
    assert "PlannerAgent" in trace_agents
    assert "MatchingAgent" in trace_agents
    assert "PricingAgent" in trace_agents
    assert "ExecutionAgent" in trace_agents
    assert "FollowUpAgent" in trace_agents

    # 8. Follow-up lifecycle schedule
    assert data["follow_up_schedule"] is not None
    assert len(data["follow_up_schedule"]) == 3
    states = [s["state"] for s in data["follow_up_schedule"]]
    assert "1-Hour Reminder" in states
    assert "En-Route Update" in states
    assert "Post-Service Completion" in states

    # 9. Dispute logs (empty on clean collision-free run)
    assert data["dispute_resolution_logs"] is not None


@patch("src.services.unified_service.GeminiIntentParser.parse_raw_query", side_effect=mock_gemini_unsupported)
def test_unified_orchestration_unsupported_service(mock_parser):
    """
    Acceptance Scenario: Unsupported / unrecognised category returns status='unsupported' with HTTP 200.
    """
    payload = {
        "query": "mujhe aik ninja chahye jo chat repair kare",
        "customer_id": "CUST-U2",
        "user_location": "DHA"
    }

    response = client.post("/api/orchestrate/run-all", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "unsupported"
    assert "AC Technician" in json_data["message"]

    agent_trace = json_data["agent_trace"]
    assert len(agent_trace) > 0
    assert any(t["agent"] == "PlannerAgent" for t in agent_trace)
