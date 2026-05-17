import logging

from src.schemas.intent import APIResponseSchema

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
    
    # Placeholder implementation
    return APIResponseSchema(
        success=False,
        error="Regex fallback not implemented yet."
    )
