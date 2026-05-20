from pydantic import BaseModel, Field
from typing import Literal

class FeedbackRequestSchema(BaseModel):
    booking_id: str
    rating: float = Field(ge=1.0, le=5.0)
    comment: str = Field(default="")

class DisputeRequestSchema(BaseModel):
    booking_id: str
    reason: Literal["no-show", "quality complaint", "price disagreement"]
    details: str = Field(default="")
