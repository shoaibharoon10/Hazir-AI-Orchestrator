import logging
import uuid
import datetime

logger = logging.getLogger(__name__)

class BookingStateError(Exception):
    """Raised when an illegal FSM state transition is attempted."""
    pass

class DoubleBookingError(Exception):
    """Raised when an identical scheduling slot is requested for an already booked provider."""
    pass

class BookingService:
    # Class-level mock in-memory state lock mapping provider_id to a list of scheduled times
    # Simulates a database unique constraint or a Redis distributed lock
    _active_provider_slots = {}
    
    # Simple deterministic valid transitions map
    VALID_TRANSITIONS = {
        "pending": ["confirmed"],
        "confirmed": ["en_route", "completed", "cancelled"], # allowing cancellation from confirmed as real-world fallback
        "en_route": ["completed"],
        "completed": [],
        "cancelled": []
    }

    def _check_double_booking(self, provider_id: str, scheduled_time: str):
        """T005: Deterministic double-booking prevention matrix (in-memory lock checking)."""
        if provider_id in self._active_provider_slots:
            if scheduled_time in self._active_provider_slots[provider_id]:
                raise DoubleBookingError(f"Provider {provider_id} is already booked for time slot {scheduled_time}.")
        else:
            self._active_provider_slots[provider_id] = set()
            
    def _lock_booking_slot(self, provider_id: str, scheduled_time: str):
        """Locks the provider for the specific time slot."""
        if provider_id not in self._active_provider_slots:
            self._active_provider_slots[provider_id] = set()
        self._active_provider_slots[provider_id].add(scheduled_time)

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
        
        # 1. Defensive validation check
        self._check_double_booking(provider_id, scheduled_time)
        
        # 2. Lock slot
        self._lock_booking_slot(provider_id, scheduled_time)
        
        booking_id = f"BKG-{uuid.uuid4().hex[:8].upper()}"
        initial_state = "pending"
        
        # Immediate state transition to confirmed (simulation flow)
        final_state = self.transition_state(booking_id, initial_state, "confirmed", request_input.customer_id)
        
        return {
            "booking_id": booking_id,
            "provider_id": provider_id,
            "current_status": final_state,
            "net_price": request_input.dynamic_price,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
