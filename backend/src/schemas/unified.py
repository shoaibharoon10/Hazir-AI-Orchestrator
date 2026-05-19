from pydantic import BaseModel
from typing import Optional

from src.schemas.intent import IntentExtractionSchema
from src.schemas.pricing import PriceBreakdownOutput
from src.schemas.booking import BookingSummaryOutput

class UnifiedOrchestratorInput(BaseModel):
    query: str
    customer_id: str
    user_location: Optional[str] = None

class UnifiedOrchestratorOutput(BaseModel):
    status: str = "success"
    agent_trace: list[dict] = []
    parsed_intent: Optional[IntentExtractionSchema] = None
    # Multi-provider options: best_match + up to 2 alternatives
    multi_provider_options: Optional[dict] = None
    # Backward-compat single provider reference (= best_match)
    assigned_provider: Optional[dict] = None
    # Itemised dynamic billing receipt
    dynamic_receipt: Optional[dict] = None
    # Standard PriceBreakdownOutput kept for test compatibility
    price_breakdown: Optional[PriceBreakdownOutput] = None
    booking_summary: Optional[BookingSummaryOutput] = None
    # Bilingual confirmation SMS draft
    client_confirmation_sms: Optional[str] = None
    follow_up_schedule: Optional[list[dict]] = None
    # Populated if DisputeAgent had to reroute
    dispute_resolution_logs: Optional[list[dict]] = None
