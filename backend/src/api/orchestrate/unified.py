import logging
import time
from typing import Union

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.schemas.intent import APIResponseSchema
from src.schemas.unified import UnifiedOrchestratorInput, UnifiedOrchestratorOutput
from src.services.unified_service import UnifiedOrchestratorService, OrchestrationError, SlotFillingError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/orchestrate",
    tags=["orchestration", "unified"],
)

unified_service = UnifiedOrchestratorService()

@router.post(
    "/run-all",
    response_model=APIResponseSchema[UnifiedOrchestratorOutput],
    summary="Master Controller: Execute Intent -> Match -> Price -> Book",
    description="Unified endpoint executing the entire end-to-end atomic workflow. Falls back and returns safe errors gracefully on collisions.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": APIResponseSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponseSchema}
    }
)
async def execute_master_workflow(request: UnifiedOrchestratorInput) -> Union[APIResponseSchema[UnifiedOrchestratorOutput], JSONResponse]:
    """
    POST endpoint to orchestrate the entire pipeline natively.
    """
    start_time = time.time()
    logger.info(f"Received master orchestration request. Query: '{request.query}'")
    
    try:
        pipeline_output = unified_service.run_pipeline(request)
        
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Total end-to-end orchestration completed successfully in {exec_time_ms}ms. Booking ID locked: {pipeline_output.booking_summary.booking_id}")
        
        return APIResponseSchema(
            success=True,
            data=pipeline_output,
            exec_time_ms=exec_time_ms
        )
        
    except SlotFillingError as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Conversational slot-filling prompted after {exec_time_ms}ms: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": e.status,
                "message": e.message,
                "exec_time_ms": exec_time_ms
            }
        )
    except OrchestrationError as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"Orchestration rollback trap triggered gracefully at stage '{e.stage}' after {exec_time_ms}ms: {e.message}")
        
        # Returning a 400 Bad Request since it's a known logic abort (e.g., 0-match, double booking)
        # We also include partial data if any stages succeeded before the abort
        error_payload = {
            "error_stage": e.stage,
            "message": e.message,
            "partial_data": e.partial_data
        }
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponseSchema(
                success=False,
                error="Pipeline transaction aborted due to orchestration error.",
                data=error_payload,
                exec_time_ms=exec_time_ms
            ).model_dump()
        )
    except Exception as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Critical unhandled exception in master pipeline after {exec_time_ms}ms: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponseSchema(
                success=False,
                error=f"Internal master orchestrator crash: {str(e)}",
                exec_time_ms=exec_time_ms
            ).model_dump()
        )
