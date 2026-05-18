import logging
import time
from typing import Union

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.schemas.intent import APIResponseSchema
from src.schemas.unified import UnifiedOrchestratorInput, UnifiedOrchestratorOutput
from src.services.unified_service import UnifiedOrchestratorService, OrchestrationError, SlotFillingError, UnsupportedServiceError

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
async def execute_master_workflow(request: UnifiedOrchestratorInput) -> JSONResponse:
    """
    POST endpoint to orchestrate the entire pipeline natively.
    Always returns HTTP 200 — status is communicated via the `status` field in the JSON body.
    """
    start_time = time.time()
    logger.info(f"Received master orchestration request. Query: '{request.query}'")
    
    try:
        pipeline_output = unified_service.run_pipeline(request)
        
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Pipeline completed in {exec_time_ms}ms. Booking ID: {pipeline_output.booking_summary.booking_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "success": True,
                "data": pipeline_output.model_dump(),
                "exec_time_ms": exec_time_ms
            }
        )

    except UnsupportedServiceError as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Unsupported service intercepted after {exec_time_ms}ms: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": e.status,
                "agent_trace": e.agent_trace,
                "message": e.message,
                "exec_time_ms": exec_time_ms
            }
        )

    except SlotFillingError as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Slot-filling prompted after {exec_time_ms}ms: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": e.status,
                "agent_trace": e.agent_trace,
                "message": e.message,
                "exec_time_ms": exec_time_ms
            }
        )

    except OrchestrationError as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"Pipeline abort at stage '{e.stage}' after {exec_time_ms}ms: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "error",
                "success": False,
                "error_stage": e.stage,
                "message": e.message,
                "exec_time_ms": exec_time_ms
            }
        )

    except Exception as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Unhandled crash after {exec_time_ms}ms: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "error",
                "success": False,
                "message": f"Internal orchestrator error: {str(e)}",
                "exec_time_ms": exec_time_ms
            }
        )
