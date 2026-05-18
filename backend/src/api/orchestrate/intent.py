import logging
import time
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
from src.lib.fallback_strategies import execute_regex_fallback

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
    start_time = time.time()
    logger.info(f"Received intent parsing request for query: '{request.query}'")
    
    # 1. Parse using Gemini
    try:
        result = intent_parser.parse_raw_query(request.query)
        if not result.success:
            logger.warning(f"Gemini API returned error: {result.error}. Triggering regex fallback.")
            result = execute_regex_fallback(request.query)
    except Exception as e:
        logger.warning(f"Gemini API exception ({type(e).__name__}): {str(e)}. Triggering regex fallback.")
        result = execute_regex_fallback(request.query)
    
    execution_time = round(time.time() - start_time, 3)
    
    if not result.success or not result.data:
        # Fallback also failed or Gemini failed completely
        logger.error(f"Intent parsing failed completely after {execution_time}s. Error: {result.error}")
        # Return 200 OK gracefully mapped back to avoid 500 crashes
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result.model_dump()
        )
        
    extracted_intent = result.data
    confidence = extracted_intent.confidence_score
    
    # 2. Implement Low-Confidence Gate Constraint (Confidence < 0.70)
    if confidence < 0.70:
        logger.warning(f"Low confidence ({confidence}) detected after {execution_time}s. Triggering clarification gate.")
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

    logger.info(f"Successfully extracted intent with high confidence ({confidence}) in {execution_time}s.")
    return result
