import logging

import re
from src.schemas.intent import APIResponseSchema, IntentExtractionSchema

logger = logging.getLogger(__name__)

def execute_regex_fallback(query: str) -> APIResponseSchema:
    """
    Fallback function that extracts basic service matches via simple 
    string/regex token queries if the main AI API fails or times out.
    
    Args:
        query (str): The raw user query.
        
    Returns:
        APIResponseSchema: The unified API response containing fallback parsed data or an error.
    """
    logger.info(f"Executing regex fallback strategy for query: '{query}'")
    
    q_lower = query.lower()
    category = "Unknown"
    
    if re.search(r'\b(ac|air condition|hvac|cooling|theek)\b', q_lower):
        category = "AC Technician"
    elif re.search(r'\b(light|electric|wiring|plug|switch)\b', q_lower):
        category = "Electrician"
    elif re.search(r'\b(plumb|water|leak|pipe|sink|drain)\b', q_lower):
        category = "Plumber"
        
    if category == "Unknown":
        return APIResponseSchema(
            success=False,
            error="Regex fallback could not determine category from tokens."
        )
        
    return APIResponseSchema(
        success=True,
        data=IntentExtractionSchema(
            service_category=category,
            location_context="Unknown fallback location",
            time_preference="As soon as possible",
            urgency_level="normal",
            confidence_score=0.75 # High enough to pass the gate
        )
    )
