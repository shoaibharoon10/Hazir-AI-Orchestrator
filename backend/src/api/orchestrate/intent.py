import logging
from typing import Union

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.nlp_helpers.gemini_parser import GeminiIntentParser
from src.schemas.intent import (
    APIResponseSchema,
    IntentErrorResponseSchema,
    IntentExtractionSchema,
    IntentRequestSchema,
)

# Set up basic logging
logger = logging.getLogger(__name__)

# Initialize the parser
intent_parser = GeminiIntentParser()

# Router configuration
router = APIRouter(
    prefix="/api/orchestrate",
    tags=["orchestration", "intent"],
)

@router.post(
    "/intent",
    response_model=APIResponseSchema[IntentExtractionSchema],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": APIResponseSchema[IntentErrorResponseSchema]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponseSchema}
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
    
    # 1. Parse using Gemini
    result = intent_parser.parse_raw_query(request.query)
    
    if not result.success or not result.data:
        # Gemini parser failed completely (e.g., API error)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=result.model_dump()
        )
        
    extracted_intent = result.data
    confidence = extracted_intent.confidence_score
    
    # 2. Implement Low-Confidence Gate Constraint (Confidence < 0.70)
    if confidence < 0.70:
        logger.warning(f"Low confidence ({confidence}) detected. Triggering clarification.")
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

    logger.info("Successfully extracted intent with high confidence.")
    return result
