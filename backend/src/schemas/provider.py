from pydantic import BaseModel, Field
from typing import List, Optional

class MatchingRequestSchema(BaseModel):
    service_category: str
    location_context: Optional[str] = None
    time_preference: Optional[str] = None
    urgency_level: str = "normal"
    
class RankedProviderResponseSchema(BaseModel):
    id: str
    name: str
    category: str
    composite_score: float = Field(ge=0.0, le=1.0)
    distance_km: float
    matched_skills: List[str]
    is_available: bool
