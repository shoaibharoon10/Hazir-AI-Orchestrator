from pydantic import BaseModel, Field
from typing import Literal

class BookingRequestInput(BaseModel):
    provider_id: str
    job_category: str
    scheduled_time: str
    dynamic_price: float = Field(ge=0.0)
    customer_id: str
    location_context: str

class BookingSummaryOutput(BaseModel):
    booking_id: str
    provider_id: str
    current_status: Literal["pending", "confirmed", "en_route", "completed", "duplicate_detected", "slot_unavailable"]
    net_price: float = Field(ge=0.0)
    timestamp: str
    external_sync: bool = False
    spreadsheet_row_id: str | None = None
    duplicate_check_performed: bool = False
    booking_lock_key: str | None = None
    provider_slot_key: str | None = None
    duplicate_detected: bool = False
    slot_available: bool = True
    external_sync_executed: bool = False
    final_booking_decision: str | None = None
    existing_booking_returned: bool = False
