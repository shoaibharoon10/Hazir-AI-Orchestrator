from pydantic import BaseModel, Field
from typing import Optional

class PricingRequestInput(BaseModel):
    job_category: str
    complexity_tier: str = Field(..., pattern="^(basic|intermediate|complex)$")
    distance_km: float = Field(ge=0.0)
    urgency_flag: bool = False
    loyalty_tier: Optional[str] = None # e.g. "silver", "gold"
    provider_base_rate: float = Field(ge=0.0)

class PriceBreakdownOutput(BaseModel):
    complexity_base_rate: float = Field(ge=0.0)
    provider_base_rate: float = Field(ge=0.0)
    urgency_surge: float = Field(ge=0.0)
    distance_charge: float = Field(ge=0.0)
    loyalty_discount: float = Field(ge=0.0)
    final_total: float = Field(ge=0.0)
