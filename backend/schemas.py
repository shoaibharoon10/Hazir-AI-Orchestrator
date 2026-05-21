from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class LocationSchema(BaseModel):
    lat: float
    lng: float

class ProviderSchema(BaseModel):
    id: str
    name: str
    category: str
    specializations: List[str] = Field(min_length=1)
    basePrice: float = Field(gt=0, description="Must be greater than 0")
    rating: float = Field(gt=0, le=5.0, description="Must be greater than 0")
    cancellationRate: float = Field(ge=0.0, le=1.0)
    reliabilityScore: float = Field(gt=0.0, le=1.0)
    distanceVectors: LocationSchema
    reviewRecency: float = Field(ge=0.0, description="Days since last review")
    isSynthetic: bool = True

class WorkingHoursSchema(BaseModel):
    start: str
    end: str

class ProviderScheduleSchema(BaseModel):
    id: str
    providerId: str
    availableDates: List[str]
    workingHours: WorkingHoursSchema
    isSynthetic: bool = True

class ReviewSchema(BaseModel):
    id: str
    providerId: str
    userId: str
    rating: float = Field(gt=0, le=5.0)
    comment: str
    timestamp: datetime
    isSynthetic: bool = True

class TimelineEntrySchema(BaseModel):
    state: str
    timestamp: datetime
    agent: str
    reasoning: Optional[str] = None

class BookingSchema(BaseModel):
    id: str
    providerId: str
    userId: str
    status: str = Field(..., pattern="^(pending|matched|confirmed|in_progress|completed|disputed|resolved)$")
    timeline: List[TimelineEntrySchema]
    isSynthetic: bool = True

class AgentTraceSchema(BaseModel):
    id: str
    bookingId: str
    agentName: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime
    isSynthetic: bool = True
