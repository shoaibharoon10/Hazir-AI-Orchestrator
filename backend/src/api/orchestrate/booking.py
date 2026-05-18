import logging
import time
from typing import Union

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.schemas.intent import APIResponseSchema
from src.schemas.booking import BookingRequestInput, BookingSummaryOutput
from src.services.booking_service import BookingService, DoubleBookingError, BookingStateError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/orchestrate",
    tags=["orchestration", "booking"],
)

booking_service = BookingService()

@router.post(
    "/book",
    response_model=APIResponseSchema[BookingSummaryOutput],
    summary="Simulate an atomic booking transaction",
    description="Transitions a scheduling request from pending to confirmed, rejecting double bookings.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": APIResponseSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponseSchema}
    }
)
async def create_booking(request: BookingRequestInput) -> Union[APIResponseSchema[BookingSummaryOutput], JSONResponse]:
    """
    POST endpoint to orchestrate final booking states.
    """
    start_time = time.time()
    logger.info(f"Received booking request for provider '{request.provider_id}' at time '{request.scheduled_time}'")
    
    try:
        booking_data = booking_service.create_booking(request)
        
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Successfully finalized booking {booking_data['booking_id']} in {exec_time_ms}ms.")
        
        return APIResponseSchema(
            success=True,
            data=booking_data
        )
        
    except DoubleBookingError as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"Double booking trapped after {exec_time_ms}ms: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponseSchema(
                success=False,
                error=str(e)
            ).model_dump()
        )
    except BookingStateError as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"State violation trapped after {exec_time_ms}ms: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponseSchema(
                success=False,
                error=str(e)
            ).model_dump()
        )
    except Exception as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Error during booking execution after {exec_time_ms}ms: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponseSchema(
                success=False,
                error=f"Internal booking engine error: {str(e)}"
            ).model_dump()
        )
