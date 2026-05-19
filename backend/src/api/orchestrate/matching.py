import logging
import time
from typing import List, Union

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.services.matching_service import ProviderMatchingEngine
from src.schemas.provider import MatchingRequestSchema, RankedProviderResponseSchema
from src.schemas.intent import APIResponseSchema

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/orchestrate",
    tags=["orchestration", "matching"],
)

matching_engine = ProviderMatchingEngine()

# Mock DB Fetch for MVP wiring
MOCK_PROVIDERS = [
    {
        "id": "prov_ac_1",
        "name": "Ali HVAC Services",
        "category": "AC Technician",
        "specializations": ["AC Installation", "AC Repair", "Maintenance"],
        "basePrice": 1500.0,
        "rating": 4.8,
        "cancellationRate": 0.05,
        "reliabilityScore": 0.92,
        "distanceVectors": {"lat": 24.8607, "lng": 67.0011},
        "reviewRecency": 2.5,
    },
    {
        "id": "prov_elec_1",
        "name": "Kamran Electrician",
        "category": "Electrician",
        "specializations": ["Wiring", "Panel Upgrades", "Fault Finding"],
        "basePrice": 1200.0,
        "rating": 4.5,
        "cancellationRate": 0.1,
        "reliabilityScore": 0.88,
        "distanceVectors": {"lat": 24.8500, "lng": 67.0100},
        "reviewRecency": 5.0,
    }
]

MOCK_SCHEDULES = [
    {"providerId": "prov_ac_1", "availableDates": ["2026-05-18"]},
    {"providerId": "prov_elec_1", "availableDates": ["2026-05-18"]}
]

@router.post(
    "/match",
    response_model=APIResponseSchema[List[RankedProviderResponseSchema]],
    summary="Match and rank providers deterministically",
    description="Applies a 6-factor deterministic algorithm to rank providers based on extracted intent."
)
async def match_providers(request: MatchingRequestSchema) -> Union[APIResponseSchema[List[RankedProviderResponseSchema]], JSONResponse]:
    """
    POST endpoint to rank providers based on multi-factor scores.
    Implements a graceful fallback mechanism preventing HTTP 500 errors if zero matches exist.
    """
    start_time = time.time()
    logger.info(f"Received matching request for category: '{request.service_category}'")
    
    try:
        result = matching_engine.match_providers(request.service_category, request.location_context or "sadar")
        best_match = result["best_match"]
        alternatives = result["alternatives"]
        
        # Combine into a flat ranked list for this endpoint's response contract
        all_results = ([best_match] if best_match else []) + list(alternatives)
        
        ranked_results = []
        for r in all_results:
            ranked_results.append(RankedProviderResponseSchema(
                id=r["provider_id"],
                name=r["name"],
                category=r["category"],
                composite_score=r["match_score"],
                distance_km=r["distance_km"],
                matched_skills=[r["category"]],
                is_available=True
            ))
        
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        
        if not ranked_results:
            logger.warning(f"No providers matched the criteria after {exec_time_ms}ms. Returning structured 0-match fallback.")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=APIResponseSchema(
                    success=True,
                    data=[],
                    error="No available providers matched your specific criteria. Please try broadening your time preference."
                ).model_dump()
            )
            
        logger.info(f"Successfully ranked {len(ranked_results)} providers in {exec_time_ms}ms.")
        return APIResponseSchema(
            success=True,
            data=ranked_results
        )
        
    except Exception as e:
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Error during matching engine execution after {exec_time_ms}ms: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponseSchema(
                success=False,
                error=f"Internal matching engine error: {str(e)}"
            ).model_dump()
        )
