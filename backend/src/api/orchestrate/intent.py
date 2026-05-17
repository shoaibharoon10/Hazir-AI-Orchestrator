import logging
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Set up basic logging
logger = logging.getLogger(__name__)

# Temporary Schemas (can be moved to backend/src/schemas/intent.py as per plan)
class IntentRequestSchema(BaseModel):
    query: str = Field(..., description="The user's raw text request (can be mixed-language/Roman Urdu)")

class IntentExtractionSchema(BaseModel):
    service_category: Literal["AC Technician", "Electrician", "Plumber"] | None = Field(
        None, description="The identified service category"
    )
    location_context: Optional[str] = Field(None, description="The location context extracted from the query")
    time_preference: Optional[str] = Field(None, description="The time preference extracted from the query")
    urgency_level: Literal["normal", "urgent", "very urgent"] | None = Field(
        "normal", description="The urgency level"
    )
    confidence_score: float = Field(..., description="Confidence score of the extraction between 0.0 and 1.0")

class IntentErrorResponseSchema(BaseModel):
    error: str = Field(..., description="Error message explaining why the request failed")
    clarifying_question: str = Field(..., description="Exactly one clarifying question for the user")

# Router configuration
router = APIRouter(
    prefix="/api/orchestrate",
    tags=["orchestration", "intent"],
)

@router.post(
    "/intent",
    response_model=IntentExtractionSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": IntentErrorResponseSchema}
    },
    summary="Parse user intent from text request",
    description="Extracts service category, location, time, and urgency from a potentially mixed-language user request."
)
async def parse_intent(request: IntentRequestSchema) -> IntentExtractionSchema:
    """
    POST endpoint to parse user intent.
    Implements the Low-Confidence Gate: if confidence < 0.70, it stops execution
    and returns exactly ONE clarifying question.
    """
    logger.info(f"Received intent parsing request for query: '{request.query}'")
    
    # TODO: Replace with actual Google Gemini API integration and parsing logic
    # For now, we simulate extraction with mock values
    
    # Simulated confidence score
    mock_confidence = 0.85
    
    # Simulate a low confidence scenario based on input
    if "help" in request.query.lower() and "ac" not in request.query.lower() and "electrician" not in request.query.lower() and "plumber" not in request.query.lower():
        mock_confidence = 0.50
        
    logger.info(f"Calculated mock confidence score: {mock_confidence}")
    
    # Implement Low-Confidence Gate Constraint (Confidence < 0.70)
    if mock_confidence < 0.70:
        logger.warning(f"Low confidence ({mock_confidence}) detected. Triggering clarification.")
        # Returning exactly ONE clarifying question as mandated
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Low confidence in parsing intent.",
                "clarifying_question": "Are you looking for an AC Technician, Electrician, or Plumber?"
            }
        )

    # Structured mock response matching Acceptance Test 1
    mock_response = IntentExtractionSchema(
        service_category="AC Technician",
        location_context="Clifton block 9",
        time_preference="today 5 PM",
        urgency_level="very urgent",
        confidence_score=mock_confidence
    )
    
    logger.info("Successfully extracted intent with high confidence.")
    return mock_response
