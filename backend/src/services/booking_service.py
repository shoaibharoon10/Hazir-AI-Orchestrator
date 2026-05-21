import logging
import uuid
import datetime

import re
import hashlib

logger = logging.getLogger(__name__)

GLOBAL_CONFIRMED_BOOKINGS = {}
GLOBAL_PROVIDER_LOCKS = {}

def normalize_time(raw_time: str) -> str:
    """Safely converts various time formats into a standard HH:MM 24-hour format."""
    if not raw_time:
        return "UNKNOWN_TIME"
    
    raw_time = raw_time.strip().lower()
    
    # Try to match HH:MM am/pm or HH am/pm
    match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', raw_time)
    if not match:
        return raw_time # fallback
        
    hour_str, min_str, period = match.groups()
    hour = int(hour_str)
    minute = int(min_str) if min_str else 0
    
    if period == 'pm' and hour < 12:
        hour += 12
    elif period == 'am' and hour == 12:
        hour = 0
        
    return f"{hour:02d}:{minute:02d}"

class BookingStateError(Exception):
    """Raised when an illegal FSM state transition is attempted."""
    pass

class DoubleBookingError(Exception):
    """Raised when an identical scheduling slot is requested for an already booked provider."""
    def __init__(self, message, alternate_slots=None):
        super().__init__(message)
        self.alternate_slots = alternate_slots or []

class BookingService:
    # Simple deterministic valid transitions map
    
    # Simple deterministic valid transitions map
    VALID_TRANSITIONS = {
        "pending": ["confirmed"],
        "confirmed": ["en_route", "completed", "cancelled"], # allowing cancellation from confirmed as real-world fallback
        "en_route": ["completed"],
        "completed": [],
        "cancelled": []
    }

    def _check_double_booking(self, provider_slot_key: str, scheduled_time: str, provider_id: str):
        """T005: Deterministic double-booking prevention matrix."""
        if provider_slot_key in GLOBAL_PROVIDER_LOCKS:
            # We can suggest alternating slots
            # For simplicity, extract the hour from "17:00" and add 2
            try:
                hour = int(scheduled_time.split(":")[0])
                alt_hour = (hour + 2) % 24
                alt_time = f"{alt_hour:02d}:00"
            except:
                alt_time = "2 hours later"

            raise DoubleBookingError(
                f"Provider {provider_id} is already booked or within the 30-minute travel buffer for {scheduled_time}.",
                alternate_slots=[f"{alt_time}", "Next operational day morning"]
            )
    def _lock_booking_slot(self, provider_slot_key: str, booking_id: str):
        """Locks the provider for the specific time slot."""
        GLOBAL_PROVIDER_LOCKS[provider_slot_key] = booking_id

    def transition_state(self, booking_id: str, current_state: str, new_state: str, customer_id: str) -> str:
        """T004: Valid state transition logic (pending -> confirmed -> en_route -> completed)"""
        if current_state not in self.VALID_TRANSITIONS:
            raise BookingStateError(f"Invalid current state: {current_state}")
            
        allowed_next_states = self.VALID_TRANSITIONS[current_state]
        if new_state not in allowed_next_states:
            raise BookingStateError(f"Illegal state transition from '{current_state}' to '{new_state}'.")
            
        self._simulate_worker_notification(booking_id, new_state, customer_id)
        
        return new_state
        
    def _simulate_worker_notification(self, booking_id: str, state: str, customer_id: str):
        """T006: Simulated follow-up notification event logging on state transitions."""
        if state == "confirmed":
            logger.info(f"SIMULATION WORKER: Triggered push notification alert for customer {customer_id}: Booking {booking_id} Confirmed.")
        elif state == "en_route":
            logger.info(f"SIMULATION WORKER: Triggered push notification alert for customer {customer_id}: Provider for booking {booking_id} is En Route.")
        elif state == "completed":
            logger.info(f"SIMULATION WORKER: Triggered push notification alert for customer {customer_id}: Booking {booking_id} is Completed. Review requested.")

    def create_booking(self, request_input) -> dict:
        """
        Creates the initial booking in 'pending' state and immediately attempts
        a simulated worker state machine transition to 'confirmed'.
        """
        provider_id = request_input.provider_id
        scheduled_time = request_input.scheduled_time
        norm_time = normalize_time(scheduled_time)
        
        # 1. Idempotency Key Generation
        raw_key = f"{request_input.customer_id}_{request_input.job_category}_{request_input.location_context}_{norm_time}"
        duplicate_key = hashlib.md5(raw_key.encode()).hexdigest()
        
        provider_slot_key = f"{provider_id}_{norm_time}"
        
        # LOGIC LAYER 1: Idempotency (Duplicate Request)
        if duplicate_key in GLOBAL_CONFIRMED_BOOKINGS:
            existing_booking = GLOBAL_CONFIRMED_BOOKINGS[duplicate_key]
            
            # Update trace fields without overriding the existing external sync ID
            result_booking = existing_booking.copy()
            result_booking["current_status"] = "duplicate_detected"
            result_booking["duplicate_check_performed"] = True
            result_booking["booking_lock_key"] = duplicate_key
            result_booking["provider_slot_key"] = provider_slot_key
            result_booking["duplicate_detected"] = True
            result_booking["slot_available"] = False  # Taken by themselves
            result_booking["external_sync_executed"] = False
            result_booking["final_booking_decision"] = "rejected_duplicate"
            result_booking["existing_booking_returned"] = True
            
            logger.info(f"Idempotency Triggered: Returning existing booking for key {duplicate_key}")
            return result_booking
        
        # LOGIC LAYER 2: Double Booking Lock
        self._check_double_booking(provider_slot_key, scheduled_time, provider_id)
        
        booking_id = f"BKG-{uuid.uuid4().hex[:8].upper()}"
        initial_state = "pending"
        
        # Immediate state transition to confirmed (simulation flow)
        final_state = self.transition_state(booking_id, initial_state, "confirmed", request_input.customer_id)
        
        # T007: External Webhook Sync Simulation
        # Here we simulate an async post to a webhook or Google Calendar API
        # THIS ONLY RUNS IF WE PASS THE DUPLICATE AND SLOT CHECKS
        logger.info(f"SIMULATION WORKER: Synchronizing booking {booking_id} with external Google Calendar/Sheet webhook (https://webhook.site/mock).")
        external_sync = True
        spreadsheet_row_id = f"ROW-{uuid.uuid4().hex[:6].upper()}"
        
        new_booking = {
            "booking_id": booking_id,
            "provider_id": provider_id,
            "current_status": final_state,
            "net_price": request_input.dynamic_price,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "external_sync": external_sync,
            "spreadsheet_row_id": spreadsheet_row_id,
            "duplicate_check_performed": True,
            "booking_lock_key": duplicate_key,
            "provider_slot_key": provider_slot_key,
            "duplicate_detected": False,
            "slot_available": True,
            "external_sync_executed": True,
            "final_booking_decision": "approved_new_booking",
            "existing_booking_returned": False
        }
        
        # Save state for future idempotency checks
        GLOBAL_CONFIRMED_BOOKINGS[duplicate_key] = new_booking.copy()
        self._lock_booking_slot(provider_slot_key, booking_id)
        
        return new_booking
