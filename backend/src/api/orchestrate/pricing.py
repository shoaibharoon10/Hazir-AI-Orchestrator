import logging
import time
from typing import Union

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.schemas.intent import APIResponseSchema
from src.schemas.pricing import PricingRequestInput, PriceBreakdownOutput
from src.services.pricing_service import PricingService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/orchestrate",
    tags=["orchestration", "pricing"],
)

pricing_service = PricingService()

@router.post(
    "/price",
    response_model=APIResponseSchema[PriceBreakdownOutput],
    summary="Calculate dynamic pricing breakdown deterministically",
    description="Applies a 5-factor mathematical formula to calculate base price, surge, distance buffer, and loyalty discounts."
)
async def calculate_price(request: PricingRequestInput) -> Union[APIResponseSchema[PriceBreakdownOutput], JSONResponse]:
    """
    POST endpoint to compute exact job pricing.
    """
    start_time = time.time()
    logger.info(f"Received pricing request for category: '{request.job_category}', tier: '{request.complexity_tier}'")
    
    try:
        breakdown = pricing_service.calculate_net_total(request)
        
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Successfully calculated pricing breakdown in {exec_time_ms}ms. Net Total: {breakdown.net_total}")
        
        return APIResponseSchema(
            success=True,
            data=breakdown
        )
        
    except Exception as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Error during pricing calculation after {exec_time_ms}ms: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponseSchema(
                success=False,
                error=f"Internal pricing engine error: {str(e)}"
            ).model_dump()
        )
