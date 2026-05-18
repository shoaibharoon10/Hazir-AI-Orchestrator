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

class SlotFillingError(Exception):
    """Custom exception for missing slots that need user clarification."""
    def __init__(self, message: str, status: str = "prompt_for_missing"):
        self.message = message
        self.status = status
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
        
        extracted_location = intent_data.location_context or request.user_location
        if not extracted_location or not extracted_location.strip() or "unknown" in extracted_location.lower():
            raise SlotFillingError("Aap ne service select ki hai, lekin location nahi batayi. Kindly Karachi ka area (e.g., Clifton, Johar, Sadar, Nazimabad, DHA) bataein taake hum kareebi options dhoond sakein.")
        
        urgency_bool = intent_data.urgency_level in ["urgent", "very urgent"]
        
        matched_providers = self.matching_engine.match_providers(intent_data.service_category, extracted_location)
        
        if not matched_providers:
            raise OrchestrationError(f"No providers found for category '{intent_data.service_category}'.", stage="matching", partial_data=output.model_dump())
            
        # top_provider = matched_providers[0]
        # output.assigned_provider = top_provider
        # provider_id = top_provider["id"]
        # distance_km = top_provider["distance_km"]

        # 1. Top ranked provider uthaein
        top_provider = matched_providers[0]

        # 2. Key Mismatch safe check (id vs provider_id)
        provider_id = top_provider.get("id") or top_provider.get("provider_id")
        distance_km = top_provider["distance_km"]

        # 3. Schema alignment dictionary taiyar karein taake validation fail na ho
        aligned_provider_data = {
            "id": provider_id,
            "name": top_provider["name"],
            "category": top_provider["category"],
            "distance_km": distance_km,
            "rating": top_provider["rating"],
            "tier": top_provider["tier"],
            "match_score": top_provider.get("match_score", 1.0)
        }
        aligned_provider_data = {
        "id": provider_id,
        "name": top_provider["name"],
        "category": top_provider["category"],
        "distance_km": distance_km,
        "rating": top_provider["rating"],
        "tier": top_provider["tier"],
        "match_score": top_provider.get("match_score", 1.0)
        }

        # 4. Output state ko data assign karein
        output.assigned_provider = aligned_provider_data


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
            urgency_flag=urgency_bool,
            loyalty_tier=None
        )
        price_breakdown = self.pricing_service.calculate_net_total(pricing_req)
        output.price_breakdown = price_breakdown
        
        # Step 4: FSM Booking Confirmation
        logger.info(f"[Unified Orchestrator] Starting booking simulation for provider {provider_id}")
        booking_req = BookingRequestInput(
            provider_id=provider_id,
            job_category=intent_data.service_category,
            scheduled_time=intent_data.time_preference or datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
