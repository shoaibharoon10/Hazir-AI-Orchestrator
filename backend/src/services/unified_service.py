import logging
import datetime

from src.nlp_helpers.gemini_parser import GeminiIntentParser
from src.lib.fallback_strategies import execute_regex_fallback

from src.schemas.unified import UnifiedOrchestratorInput, UnifiedOrchestratorOutput
from src.schemas.provider import MatchingRequestSchema
from src.schemas.pricing import PricingRequestInput
from src.schemas.booking import BookingRequestInput, BookingSummaryOutput

from src.services.matching_service import ProviderMatchingEngine
from src.services.pricing_service import PricingService
from src.services.booking_service import BookingService, DoubleBookingError

logger = logging.getLogger(__name__)

class OrchestrationError(Exception):
    """Custom exception for controlled pipeline aborts."""
    def __init__(self, message: str, stage: str, partial_data: dict = None):
        self.message = message
        self.stage = stage
        self.partial_data = partial_data
        super().__init__(self.message)

class UnifiedOrchestratorService:
    def __init__(self):
        self.intent_parser = GeminiIntentParser()
        self.matching_engine = ProviderMatchingEngine()
        self.pricing_service = PricingService()
        self.booking_service = BookingService()
        
        # Mocks for E2E wiring
        self.MOCK_PROVIDERS = [
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
        self.MOCK_SCHEDULES = [
            {"providerId": "prov_ac_1", "availableDates": ["2026-05-18"]},
            {"providerId": "prov_elec_1", "availableDates": ["2026-05-18"]}
        ]

    def run_pipeline(self, request: UnifiedOrchestratorInput) -> UnifiedOrchestratorOutput:
        output = UnifiedOrchestratorOutput()
        
        # Step 1: Intent Extraction
        logger.info(f"[Unified Orchestrator] Starting intent extraction for query: '{request.query}'")
        try:
            intent_result = self.intent_parser.parse_raw_query(request.query)
            if not intent_result.success or not intent_result.data:
                logger.warning("[Unified Orchestrator] Gemini parse failed. Triggering fallback.")
                intent_result = execute_regex_fallback(request.query)
        except Exception as e:
            logger.warning(f"[Unified Orchestrator] Gemini exception: {str(e)}. Triggering fallback.")
            intent_result = execute_regex_fallback(request.query)
            
        if not intent_result.success or not intent_result.data:
            raise OrchestrationError("Could not extract intent from query.", stage="intent")
            
        intent_data = intent_result.data
        if intent_data.confidence_score < 0.70:
            raise OrchestrationError("Low confidence in intent parsing. Clarification required.", stage="intent")
            
        output.parsed_intent = intent_data
        
        # Step 2: Provider Matching
        logger.info(f"[Unified Orchestrator] Starting provider matching for category: {intent_data.service_category}")
        
        candidates = [p for p in self.MOCK_PROVIDERS if p.get('category') == intent_data.service_category]
        schedules = [s for s in self.MOCK_SCHEDULES if s.get('providerId') in [c['id'] for c in candidates]]
        
        matching_req = MatchingRequestSchema(
            service_category=intent_data.service_category,
            user_location=request.user_location,
            required_time_slot=intent_data.preferred_time_slot,
            urgency_flag=intent_data.urgency_flag
        )
        
        matched_providers = self.matching_engine.match_and_rank(matching_req, candidates, schedules)
        
        if not matched_providers:
            raise OrchestrationError(f"No providers found for category '{intent_data.service_category}'.", stage="matching", partial_data=output.model_dump())
            
        top_provider = matched_providers[0]
        output.assigned_provider = top_provider.model_dump()
        provider_id = top_provider.provider_id
        distance_km = top_provider.calculated_distance_km
        
        # Step 3: Dynamic Pricing
        logger.info(f"[Unified Orchestrator] Starting price calculation for provider: {provider_id}")
        
        complexity_tier = "intermediate"
        if "ac" in intent_data.service_category.lower() or "complex" in intent_data.service_category.lower():
            complexity_tier = "complex"
        elif "clean" in intent_data.service_category.lower() or "basic" in intent_data.service_category.lower():
            complexity_tier = "basic"
            
        pricing_req = PricingRequestInput(
            job_category=intent_data.service_category,
            complexity_tier=complexity_tier,
            distance_km=distance_km,
            urgency_flag=intent_data.urgency_flag,
            loyalty_tier=None
        )
        price_breakdown = self.pricing_service.calculate_net_total(pricing_req)
        output.price_breakdown = price_breakdown
        
        # Step 4: FSM Booking Confirmation
        logger.info(f"[Unified Orchestrator] Starting booking simulation for provider {provider_id}")
        booking_req = BookingRequestInput(
            provider_id=provider_id,
            job_category=intent_data.service_category,
            scheduled_time=intent_data.preferred_time_slot or datetime.datetime.now(datetime.timezone.utc).isoformat(),
            dynamic_price=price_breakdown.net_total,
            customer_id=request.customer_id,
            location_context=request.user_location
        )
        
        try:
            booking_summary_dict = self.booking_service.create_booking(booking_req)
            output.booking_summary = BookingSummaryOutput(**booking_summary_dict)
        except DoubleBookingError as e:
            raise OrchestrationError(f"Double booking collision trapped: {str(e)}", stage="booking", partial_data=output.model_dump())
        except Exception as e:
            raise OrchestrationError(f"Booking error: {str(e)}", stage="booking", partial_data=output.model_dump())
            
        logger.info("[Unified Orchestrator] End-to-end pipeline completed successfully.")
        return output
