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
    def __init__(self, message: str, agent_trace: list, status: str = "prompt_for_missing"):
        self.message = message
        self.status = status
        self.agent_trace = agent_trace
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
        agent_trace = []
        
        # Agent 1: PlannerAgent
        agent_trace.append({"agent": "PlannerAgent", "thought": "Extracting entities from raw user query", "action": "Invoked GeminiIntentParser"})
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
        
        # PlannerAgent multi-turn slot filling check
        agent_trace.append({"agent": "PlannerAgent", "thought": "Validating mandatory slots: category, location, time", "action": "Performing Slot-Filling Check"})
        extracted_location = intent_data.location_context or request.user_location
        
        if not intent_data.service_category:
            agent_trace.append({"agent": "PlannerAgent", "thought": "Service category slot is missing", "action": "Triggered Slot-Filling Error"})
            raise SlotFillingError("Aapko kaunsi service chahye? Kindly specify karein (e.g., Plumber, AC Technician, etc.).", agent_trace=agent_trace)

        loc_missing = not extracted_location or not extracted_location.strip() or "unknown" in extracted_location.lower()
        time_missing = not intent_data.time_preference
        
        if loc_missing and time_missing:
            agent_trace.append({"agent": "PlannerAgent", "thought": "Both location and time slots are missing", "action": "Triggered Slot-Filling Error"})
            raise SlotFillingError("Aap ne service select ki hai, lekin location aur time nahi bataya. Kindly apna area (e.g., Clifton, Johar) aur time bataein.", agent_trace=agent_trace)
            
        if loc_missing:
            agent_trace.append({"agent": "PlannerAgent", "thought": "Location slot is missing or invalid", "action": "Triggered Slot-Filling Error"})
            raise SlotFillingError("Aap ne service select ki hai, lekin location (area) nahi batayi. Kindly Karachi ka area (e.g., Clifton, Johar, Sadar, Nazimabad, DHA) bataein taake hum kareebi options dhoond sakein.", agent_trace=agent_trace)
            
        if time_missing:
             agent_trace.append({"agent": "PlannerAgent", "thought": "Time slot is missing", "action": "Triggered Slot-Filling Error"})
             raise SlotFillingError("Aap ne service select ki hai, lekin time nahi bataya. Kindly bataein aapko technician kab chahiye?", agent_trace=agent_trace)
        
        # Agent 2: MatchingAgent
        agent_trace.append({"agent": "MatchingAgent", "thought": f"Calculating Euclidean distances for {intent_data.service_category} candidates near {extracted_location}", "action": "Invoked Geospatial Matching"})
        logger.info(f"[Unified Orchestrator] Starting provider matching for category: {intent_data.service_category}")
        
        urgency_bool = intent_data.urgency_level in ["urgent", "very urgent"]
        
        matched_providers = self.matching_engine.match_providers(intent_data.service_category, extracted_location)
        
        if not matched_providers:
            raise OrchestrationError(f"No providers found for category '{intent_data.service_category}'.", stage="matching", partial_data=output.model_dump())
            
        top_provider = matched_providers[0]
        provider_id = top_provider.get("id") or top_provider.get("provider_id")
        distance_km = top_provider["distance_km"]
        
        agent_trace.append({"agent": "MatchingAgent", "thought": f"Selected provider {provider_id} based on optimal geospatial mapping.", "action": "Matched Top Provider"})

        aligned_provider_data = {
            "id": provider_id,
            "name": top_provider["name"],
            "category": top_provider["category"],
            "distance_km": distance_km,
            "rating": top_provider["rating"],
            "tier": top_provider["tier"],
            "match_score": top_provider.get("match_score", 1.0),
            "selection_reasoning": top_provider.get("selection_reasoning", f"Selected '{top_provider['name']}' because they are the closest available {top_provider['tier'].capitalize()}-Tier provider within {distance_km}km with a {top_provider['rating']} rating.")
        }
        
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
        
        agent_trace.append({"agent": "PricingAgent", "thought": f"Calculating dynamic surge and base pricing for {complexity_tier} tier with {distance_km}km distance", "action": "Computed Net Total"})
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
            
        # Agent 3: LifecycleAgent
        agent_trace.append({"agent": "LifecycleAgent", "thought": "Booking confirmed, scheduling FSM simulation states", "action": "Generated future lifecycle schedule"})
        
        now = datetime.datetime.now(datetime.timezone.utc)
        output.follow_up_schedule = [
            {"state": "1-Hour Reminder", "timestamp": (now + datetime.timedelta(hours=1)).isoformat(), "message": "Reminder: Your technician will arrive in 1 hour."},
            {"state": "En-Route", "timestamp": (now + datetime.timedelta(hours=2)).isoformat(), "message": "Alert: The technician is en-route to your location."},
            {"state": "Post-Service Completion", "timestamp": (now + datetime.timedelta(hours=4)).isoformat(), "message": "Confirmation: Service marked as completed. Please leave a review."}
        ]
        
        output.agent_trace = agent_trace
        logger.info("[Unified Orchestrator] End-to-end pipeline completed successfully.")
        return output
