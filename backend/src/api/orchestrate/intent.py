import logging
from typing import Union

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.schemas.intent import (
    APIResponseSchema,
    IntentErrorResponseSchema,
    IntentExtractionSchema,
    IntentRequestSchema,
)

# Set up basic logging
logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/api/orchestrate",
    tags=["orchestration", "intent"],
)

@router.post(
    "/intent",
    response_model=APIResponseSchema[IntentExtractionSchema],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": APIResponseSchema[IntentErrorResponseSchema]}
    },
    summary="Parse user intent from text request",
    description="Extracts service category, location, time, and urgency from a potentially mixed-language user request."
)
async def parse_intent(request: IntentRequestSchema) -> Union[APIResponseSchema[IntentExtractionSchema], JSONResponse]:
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
        error_data = IntentErrorResponseSchema(
            error="Low confidence in parsing intent.",
            clarifying_question="Are you looking for an AC Technician, Electrician, or Plumber?"
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponseSchema(
                success=False,
                data=error_data.model_dump(),
                error="Low confidence gate triggered"
            ).model_dump()
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
    return APIResponseSchema(
        success=True,
        data=mock_response
    )
