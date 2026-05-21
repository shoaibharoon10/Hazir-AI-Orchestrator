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
    
    agent_trace = []
    agent_trace.append({
        "agent": "FollowUpAgent",
        "thought": f"Received {request.rating}-star rating for booking '{request.booking_id}' (Provider: {request.provider_id}). Processing reputation update.",
        "action": "Feedback Recorded"
    })
    
    logger.info(f"SIMULATION WORKER: Provider {request.provider_id} rating updated with new {request.rating}-star review.")
    
    agent_trace.append({
        "agent": "FollowUpAgent",
        "thought": "Simulated dynamic reputation recalculation in database.",
        "action": "Reputation Update Simulated"
    })
    
    exec_time_ms = round((time.time() - start_time) * 1000, 2)
    return APIResponseSchema(
        success=True,
        data={
            "status": "feedback recorded",
            "message": "reputation update simulated",
            "booking_id": request.booking_id,
            "provider_id": request.provider_id
        },
        agent_trace=agent_trace,
        exec_time_ms=exec_time_ms
    )

@router.post(
    "/dispute",
    response_model=APIResponseSchema,
    summary="Simulate dispute escalation workflow",
)
async def submit_dispute(request: DisputeRequestSchema):
    start_time = time.time()
    
    agent_trace = []
    agent_trace.append({
        "agent": "DisputeAgent",
        "thought": f"Received dispute for booking '{request.booking_id}' against Provider '{request.provider_id}'. Reason: {request.reason}.",
        "action": "Dispute Logged"
    })
    
    # Mock escalation logic
    resolution = "under review"
    action_taken = ""
    if request.reason == "no-show":
        logger.warning(f"SIMULATION WORKER: Provider no-show detected for {request.booking_id}. Auto-initiating refund.")
        resolution = "refund initiated"
        action_taken = "Provider reliability penalty applied"
    elif request.reason == "quality complaint":
        logger.warning(f"SIMULATION WORKER: Quality complaint lodged for {request.booking_id}. Escalated to QA team.")
        resolution = "escalated to QA"
        action_taken = "QA review scheduled"
    elif request.reason == "price disagreement":
        logger.warning(f"SIMULATION WORKER: Price dispute for {request.booking_id}. Freezing payment.")
        resolution = "payment frozen"
        action_taken = "Human review requested"
        
    agent_trace.append({
        "agent": "DisputeAgent",
        "thought": f"Evaluating '{request.reason}' constraint. Triggering corresponding safety protocol.",
        "action": f"Resolution: {resolution} / {action_taken}"
    })
        
    exec_time_ms = round((time.time() - start_time) * 1000, 2)
    return APIResponseSchema(
        success=True,
        data={
            "booking_id": request.booking_id, 
            "provider_id": request.provider_id,
            "status": "disputed", 
            "resolution_state": resolution,
            "simulated_action": action_taken
        },
        agent_trace=agent_trace,
        exec_time_ms=exec_time_ms
    )
