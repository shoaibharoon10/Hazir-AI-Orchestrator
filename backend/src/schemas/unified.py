from pydantic import BaseModel
from typing import Optional

from src.schemas.intent import IntentExtractionSchema
from src.schemas.pricing import PriceBreakdownOutput
from src.schemas.booking import BookingSummaryOutput

class UnifiedOrchestratorInput(BaseModel):
    query: str
    customer_id: str
    user_location: str

class UnifiedOrchestratorOutput(BaseModel):
    parsed_intent: Optional[IntentExtractionSchema] = None
    assigned_provider: Optional[dict] = None
    price_breakdown: Optional[PriceBreakdownOutput] = None
    booking_summary: Optional[BookingSummaryOutput] = None
