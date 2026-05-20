from typing import Any, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

class APIResponseSchema(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    exec_time_ms: Optional[float] = None

class IntentRequestSchema(BaseModel):
    query: str = Field(..., description="The user's raw text request (can be mixed-language/Roman Urdu)")

class IntentExtractionSchema(BaseModel):
    service_category: Literal["AC Technician", "Electrician", "Plumber", "Beautician", "Appliance Repair", "Tutor"] | None = Field(
        None, description="The identified service category"
    )
    location_context: Optional[str] = Field(None, description="The location context extracted from the query")
    time_preference: Optional[str] = Field(None, description="The time preference extracted from the query")
    urgency_level: Literal["normal", "urgent", "very urgent"] | None = Field(
        "normal", description="The urgency level"
    )
    confidence_score: float = Field(..., description="Confidence score of the extraction between 0.0 and 1.0")

class IntentErrorResponseSchema(BaseModel):
    error: str = Field(..., description="Error message explaining why the request failed")
    clarifying_question: str = Field(..., description="Exactly one clarifying question for the user")
