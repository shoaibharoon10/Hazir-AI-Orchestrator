from pydantic import BaseModel, Field
from typing import Optional

class PricingRequestInput(BaseModel):
    job_category: str
    complexity_tier: str = Field(..., pattern="^(basic|intermediate|complex)$")
    distance_km: float = Field(ge=0.0)
    urgency_flag: bool = False
    loyalty_tier: Optional[str] = None # e.g. "silver", "gold"

class PriceBreakdownOutput(BaseModel):
    base_price: float = Field(ge=0.0)
    surge_cost: float = Field(ge=0.0)
    distance_buffer: float = Field(ge=0.0)
    discount: float = Field(ge=0.0)
    net_total: float = Field(ge=0.0)
