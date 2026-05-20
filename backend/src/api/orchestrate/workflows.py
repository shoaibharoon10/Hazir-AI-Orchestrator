import logging
import time
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.schemas.intent import APIResponseSchema
from src.schemas.workflows import FeedbackRequestSchema, DisputeRequestSchema

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/orchestrate",
    tags=["orchestration", "workflows"],
)

@router.post(
    "/feedback",
    response_model=APIResponseSchema,
    summary="Simulate provider feedback submission",
)
async def submit_feedback(request: FeedbackRequestSchema):
    start_time = time.time()
    logger.info(f"Received feedback for booking '{request.booking_id}' with rating {request.rating}")
    
    # Simulate updating provider rating and appending to trace
    logger.info(f"SIMULATION WORKER: Provider rating updated with new {request.rating}-star review.")
    
    exec_time_ms = round((time.time() - start_time) * 1000, 2)
    return APIResponseSchema(
        success=True,
        data={"booking_id": request.booking_id, "status": "feedback_recorded", "new_average": request.rating},
        exec_time_ms=exec_time_ms
    )

@router.post(
    "/dispute",
    response_model=APIResponseSchema,
    summary="Simulate dispute escalation workflow",
)
async def submit_dispute(request: DisputeRequestSchema):
    start_time = time.time()
    logger.info(f"Received dispute for booking '{request.booking_id}', reason: {request.reason}")
    
    # Mock escalation logic
    resolution = "under review"
    if request.reason == "no-show":
        logger.warning(f"SIMULATION WORKER: Provider no-show detected for {request.booking_id}. Auto-initiating refund.")
        resolution = "refund initiated"
    elif request.reason == "quality complaint":
        logger.warning(f"SIMULATION WORKER: Quality complaint lodged for {request.booking_id}. Escalated to QA team.")
        resolution = "escalated to QA"
    elif request.reason == "price disagreement":
        logger.warning(f"SIMULATION WORKER: Price dispute for {request.booking_id}. Freezing payment.")
        resolution = "payment frozen"
        
    exec_time_ms = round((time.time() - start_time) * 1000, 2)
    return APIResponseSchema(
        success=True,
        data={
            "booking_id": request.booking_id, 
            "status": "disputed", 
            "resolution_state": resolution
        },
        exec_time_ms=exec_time_ms
    )
