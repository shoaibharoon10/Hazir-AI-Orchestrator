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
    current_status: Literal["pending", "confirmed", "en_route", "completed"]
    net_price: float = Field(ge=0.0)
    timestamp: str
