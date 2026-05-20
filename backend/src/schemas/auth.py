from pydantic import BaseModel, Field
from typing import List, Dict

class ProviderRegisterSchema(BaseModel):
    name: str = Field(..., description="Provider's full name")
    email: str = Field(..., description="Provider's email address")
    phone: str = Field(..., description="Provider's phone number")
    password: str = Field(..., description="Provider's raw password")
    address: str = Field(..., description="Provider's address")
    city: str = Field(..., description="Provider's city")
    category: str = Field(..., description="Service category (e.g., Plumber, AC Technician)")
    base_price: float = Field(..., description="Base fee for the service")
    specializations: List[str] = Field(..., description="List of specific skills or specializations")
    working_hours: Dict[str, str] = Field(..., description="Dictionary with 'start' and 'end' times")
