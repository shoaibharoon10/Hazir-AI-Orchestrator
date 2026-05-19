import logging
import datetime

from src.nlp_helpers.gemini_parser import GeminiIntentParser
from src.lib.fallback_strategies import execute_regex_fallback

from src.schemas.unified import UnifiedOrchestratorInput, UnifiedOrchestratorOutput
from src.schemas.pricing import PricingRequestInput
from src.schemas.booking import BookingRequestInput, BookingSummaryOutput

from src.services.matching_service import ProviderMatchingEngine
from src.services.pricing_service import PricingService
from src.services.booking_service import BookingService, DoubleBookingError

logger = logging.getLogger(__name__)

ALLOWED_CATEGORIES = ["AC Technician", "Plumber", "Electrician", "Beautician", "Appliance Repair"]


# ---------------------------------------------------------------------------
# Custom pipeline exceptions
# ---------------------------------------------------------------------------

class OrchestrationError(Exception):
    """Controlled pipeline abort with stage metadata."""
    def __init__(self, message: str, stage: str, partial_data: dict = None):
        self.message = message
        self.stage = stage
        self.partial_data = partial_data
        super().__init__(self.message)


class SlotFillingError(Exception):
    """Missing mandatory slot — needs user clarification."""
    def __init__(self, message: str, agent_trace: list, status: str = "prompt_for_missing"):
        self.message = message
        self.status = status
        self.agent_trace = agent_trace
        super().__init__(self.message)


class UnsupportedServiceError(Exception):
    """Parsed category not in the five supported verticals."""
    def __init__(self, message: str, agent_trace: list, status: str = "unsupported"):
        self.message = message
        self.status = status
        self.agent_trace = agent_trace
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Orchestrator Service
# ---------------------------------------------------------------------------

class UnifiedOrchestratorService:
    def __init__(self):
        self.intent_parser = GeminiIntentParser()
        self.matching_engine = ProviderMatchingEngine()
        self.pricing_service = PricingService()
        self.booking_service = BookingService()

    # -----------------------------------------------------------------------
    # Master pipeline
    # -----------------------------------------------------------------------

    def run_pipeline(self, request: UnifiedOrchestratorInput) -> UnifiedOrchestratorOutput:
        output = UnifiedOrchestratorOutput()
        agent_trace = []

        # ===================================================================
        # Agent 1 — PlannerAgent: Multilingual Intent Extraction + Slot Gate
        # ===================================================================
        agent_trace.append({
            "agent": "PlannerAgent",
            "thought": "Extracting structured intent from multilingual query (Urdu / Roman Urdu / English)",
            "action": "Invoked GeminiIntentParser",
            "tool_used": "GeminiIntentParser"
        })
        logger.info(f"[PlannerAgent] Query: '{request.query}'")

        try:
            intent_result = self.intent_parser.parse_raw_query(request.query)
            if not intent_result.success or not intent_result.data:
                logger.warning("[PlannerAgent] Gemini failed — triggering regex fallback.")
                intent_result = execute_regex_fallback(request.query)
        except Exception as exc:
            logger.warning(f"[PlannerAgent] Gemini exception: {exc} — triggering regex fallback.")
            intent_result = execute_regex_fallback(request.query)

        if not intent_result.success or not intent_result.data:
            agent_trace.append({
                "agent": "PlannerAgent",
                "thought": "Both Gemini and regex fallback failed to extract any intent",
                "action": "Triggered Slot-Filling Error (total failure)"
            })
            raise SlotFillingError(
                "Maazrat, main aap ki baat samajh nahi paya. Kya aap bata sakte hain "
                "aap ko konsi service (AC, Plumber, Electrician, Beautician) chahiye?",
                agent_trace=agent_trace
            )

        intent_data = intent_result.data
        if intent_data.confidence_score < 0.70:
            agent_trace.append({
                "agent": "PlannerAgent",
                "thought": f"Confidence score {intent_data.confidence_score} is below 0.70 threshold",
                "action": "Triggered Slot-Filling Error (low confidence)"
            })
            raise SlotFillingError(
                "Maazrat, main aap ki baat samajh nahi paya. Kya aap bata sakte hain "
                "aap ko konsi service (AC, Plumber, Electrician, Beautician) chahiye?",
                agent_trace=agent_trace
            )

        output.parsed_intent = intent_data

        # Slot validation
        agent_trace.append({
            "agent": "PlannerAgent",
            "thought": "Concurrently validating 3 mandatory slots: service_category, location_text, scheduled_time",
            "action": "Performing Slot-Filling Check"
        })

        # Strict coercion: empty strings, whitespace, "unknown", "--" all become None
        def _coerce_slot(val):
            if not val or not val.strip():
                return None
            cleaned = val.strip().lower()
            if cleaned in ("unknown", "--", "unknown fallback location", "n/a", "none"):
                return None
            return val.strip()

        extracted_location = _coerce_slot(intent_data.location_context) or _coerce_slot(request.user_location)
        extracted_time = _coerce_slot(intent_data.time_preference)

        # STEP A — Unsupported service guard (fires before location/time)
        if not intent_data.service_category or intent_data.service_category not in ALLOWED_CATEGORIES:
            agent_trace.append({
                "agent": "PlannerAgent",
                "thought": f"Category '{intent_data.service_category}' is outside the five supported verticals",
                "action": "Triggered UnsupportedServiceError"
            })
            raise UnsupportedServiceError(
                "Maazrat! Hamare paas filhal yeh service operational nahi hai. "
                "Currently hum Karachi mein sirf in core vertical services ke sath deal kar rahe hain: "
                "AC Technician, Plumber, Electrician, Beautician, aur Appliance Repair.",
                agent_trace=agent_trace
            )

        # STEP B — Location is always checked before time
        loc_missing = not extracted_location
        time_missing = not extracted_time

        if loc_missing and time_missing:
            agent_trace.append({
                "agent": "PlannerAgent",
                "thought": "Both location and time slots are absent",
                "action": "Triggered Slot-Filling Error (both)"
            })
            raise SlotFillingError(
                "Aap ne service select ki hai, lekin location aur time dono nahi bataye. "
                "Kindly apna Karachi area (e.g., Clifton, Johar, DHA) aur preferred time bataein.",
                agent_trace=agent_trace
            )

        if loc_missing:
            agent_trace.append({
                "agent": "PlannerAgent",
                "thought": "Location slot missing — blocking pipeline regardless of time slot state",
                "action": "Triggered Slot-Filling Error (location)"
            })
            raise SlotFillingError(
                "Aap ne service select ki hai, lekin location (area) nahi batayi. "
                "Kindly Karachi ka area (e.g., Clifton, Johar, Sadar, Nazimabad, DHA) bataein "
                "taake hum kareebi options dhoond sakein.",
                agent_trace=agent_trace
            )

        if time_missing:
            agent_trace.append({
                "agent": "PlannerAgent",
                "thought": "Time slot missing",
                "action": "Triggered Slot-Filling Error (time)"
            })
            raise SlotFillingError(
                "Aap ne service select ki hai, lekin time nahi bataya. "
                "Kindly bataein aapko technician kab chahiye?",
                agent_trace=agent_trace
            )

        agent_trace.append({
            "agent": "PlannerAgent",
            "thought": "All 3 mandatory slots verified. Handing off to MatchingAgent.",
            "action": "Slot Validation Passed"
        })

        # ===================================================================
        # Agent 2 — MatchingAgent: Geospatial Multi-Option Ranking
        # ===================================================================
        urgency_bool = intent_data.urgency_level in ["urgent", "very urgent"]

        agent_trace.append({
            "agent": "MatchingAgent",
            "thought": (
                f"Computing Euclidean distance vectors for all '{intent_data.service_category}' "
                f"providers near '{extracted_location}'. Ranking by proximity + tier weight."
            ),
            "action": "Invoked Geospatial Matching Engine",
            "tool_used": "ProviderMatchingEngine"
        })

        match_result = self.matching_engine.match_providers(
            intent_data.service_category, extracted_location
        )

        if not match_result["best_match"]:
            raise OrchestrationError(
                f"No providers found for category '{intent_data.service_category}'.",
                stage="matching",
                partial_data=output.model_dump()
            )

        best_match = match_result["best_match"]
        alternatives = match_result["alternatives"]
        distance_km = best_match["distance_km"]

        output.multi_provider_options = match_result
        output.assigned_provider = {
            "id": best_match["provider_id"],
            "name": best_match["name"],
            "category": best_match["category"],
            "distance_km": distance_km,
            "rating": best_match["rating"],
            "tier": best_match["tier"],
            "match_score": best_match["match_score"],
            "selection_reasoning": best_match["selection_reasoning"]
        }

        agent_trace.append({
            "agent": "MatchingAgent",
            "thought": (
                f"Best match: '{best_match['name']}' @ {distance_km}km. "
                f"{len(alternatives)} alternative(s) available."
            ),
            "action": "Multi-Option Ranking Complete"
        })

        # ===================================================================
        # Agent 3 — PricingAgent: Dynamic Billing Receipt
        # ===================================================================
        complexity_tier = "intermediate"
        cat_lower = intent_data.service_category.lower()
        if "ac" in cat_lower:
            complexity_tier = "complex"
        elif "beautician" in cat_lower or "appliance" in cat_lower:
            complexity_tier = "basic"

        agent_trace.append({
            "agent": "PricingAgent",
            "thought": (
                f"Computing dynamic pricing for '{complexity_tier}' complexity, "
                f"{distance_km}km distance, urgency={urgency_bool}."
            ),
            "action": "Calculated Net Total",
            "tool_used": "PricingService"
        })

        pricing_req = PricingRequestInput(
            job_category=intent_data.service_category,
            complexity_tier=complexity_tier,
            distance_km=distance_km,
            urgency_flag=urgency_bool,
            loyalty_tier=None
        )
        price_breakdown = self.pricing_service.calculate_net_total(pricing_req)
        output.price_breakdown = price_breakdown
        output.dynamic_receipt = {
            "base_fee": price_breakdown.base_price,
            "distance_fee": price_breakdown.distance_buffer,
            "urgency_surge": price_breakdown.surge_cost,
            "discount": price_breakdown.discount,
            "grand_total": price_breakdown.net_total
        }

        # ===================================================================
        # Agent 4 — ExecutionAgent + DisputeAgent: FSM Booking + Collision Handling
        # ===================================================================
        agent_trace.append({
            "agent": "ExecutionAgent",
            "thought": (
                f"Attempting slot lock for best_match '{best_match['name']}' "
                f"at time '{extracted_time}'."
            ),
            "action": "Initiating Booking FSM",
            "tool_used": "BookingService"
        })

        dispute_resolution_logs = []
        booking_summary_dict = None
        booked_provider = None

        # Build ordered candidate list: best_match first, then alternatives
        all_candidates = [best_match] + list(alternatives)

        for idx, candidate in enumerate(all_candidates):
            candidate_id = candidate["provider_id"]
            try:
                booking_req = BookingRequestInput(
                    provider_id=candidate_id,
                    job_category=intent_data.service_category,
                    scheduled_time=extracted_time,
                    dynamic_price=price_breakdown.net_total,
                    customer_id=request.customer_id,
                    location_context=extracted_location
                )
                booking_summary_dict = self.booking_service.create_booking(booking_req)
                booked_provider = candidate

                if idx == 0:
                    agent_trace.append({
                        "agent": "ExecutionAgent",
                        "thought": f"Slot locked for best_match '{candidate['name']}'.",
                        "action": "Booking Confirmed"
                    })
                else:
                    agent_trace.append({
                        "agent": "DisputeAgent",
                        "thought": (
                            f"Alternative #{idx} '{candidate['name']}' successfully booked "
                            f"after {idx} collision(s)."
                        ),
                        "action": "Dispute Resolved — Alternative Booked"
                    })
                break  # booking succeeded

            except DoubleBookingError as dbe:
                log_entry = {
                    "attempt_index": idx,
                    "provider_id": candidate_id,
                    "provider_name": candidate["name"],
                    "collision_reason": str(dbe),
                    "action": "Routing to next candidate"
                }
                dispute_resolution_logs.append(log_entry)
                logger.warning(f"[DisputeAgent] Collision on candidate #{idx} '{candidate['name']}': {dbe}")

                if idx == 0:
                    agent_trace.append({
                        "agent": "DisputeAgent",
                        "thought": (
                            f"Double-booking collision on best_match '{candidate['name']}'. "
                            "Activating sequential alternative resolution."
                        ),
                        "action": "Dispute Initiated — Iterating Alternatives"
                    })
                else:
                    agent_trace.append({
                        "agent": "DisputeAgent",
                        "thought": f"Collision on alternative #{idx} '{candidate['name']}'. Evaluating next.",
                        "action": "Evaluating Next Candidate"
                    })

            except Exception as exc:
                raise OrchestrationError(
                    f"Unexpected booking error: {str(exc)}",
                    stage="booking",
                    partial_data=output.model_dump()
                )

        if booking_summary_dict is None:
            agent_trace.append({
                "agent": "DisputeAgent",
                "thought": f"All {len(all_candidates)} candidates exhausted. Request unfulfillable.",
                "action": "Dispute Unresolved"
            })
            raise OrchestrationError(
                f"All {len(all_candidates)} providers are already booked for the requested slot.",
                stage="booking",
                partial_data=output.model_dump()
            )

        output.booking_summary = BookingSummaryOutput(**booking_summary_dict)
        output.dispute_resolution_logs = dispute_resolution_logs

        # Build bilingual confirmation SMS
        output.client_confirmation_sms = (
            f"Booking Confirmed! Apka {intent_data.service_category} provider "
            f"'{booked_provider['name']}' assign ho chuka hai. "
            f"Booking ID: {booking_summary_dict['booking_id']}. "
            f"Scheduled: {intent_data.time_preference}. "
            f"Location: {extracted_location}. "
            f"Total Amount: PKR {price_breakdown.net_total:.2f}. "
            f"Shukriya! — AI Service Orchestrator"
        )

        # ===================================================================
        # Agent 5 — FollowUpAgent: Timestamped Lifecycle Automation
        # ===================================================================
        now = datetime.datetime.now(datetime.timezone.utc)
        output.follow_up_schedule = [
            {
                "state": "1-Hour Reminder",
                "timestamp": (now + datetime.timedelta(hours=1)).isoformat(),
                "message": (
                    f"Reminder: Aapka technician '{booked_provider['name']}' "
                    "1 ghante mein pahunch jayega. Please tayyar rahein."
                )
            },
            {
                "state": "En-Route Update",
                "timestamp": (now + datetime.timedelta(hours=2)).isoformat(),
                "message": (
                    f"Alert: Provider '{booked_provider['name']}' ab aapki taraf aa raha hai. "
                    "Live coordinate tracking active."
                )
            },
            {
                "state": "Post-Service Completion",
                "timestamp": (now + datetime.timedelta(hours=4)).isoformat(),
                "message": (
                    f"Service complete! Booking {booking_summary_dict['booking_id']} "
                    "successfully mark ho gaya. Feedback zaroor dein — shukriya!"
                )
            }
        ]

        agent_trace.append({
            "agent": "FollowUpAgent",
            "thought": "Booking confirmed. Generating 3-stage automated lifecycle notification schedule.",
            "action": "Follow-Up Schedule Generated"
        })

        output.agent_trace = agent_trace
        logger.info(
            f"[Orchestrator] Pipeline complete. Booking {booking_summary_dict['booking_id']} "
            f"locked for provider '{booked_provider['name']}'."
        )
        return output
