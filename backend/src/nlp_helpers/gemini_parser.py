import json
import logging
import os
import time
from typing import Any, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from pydantic import ValidationError

from src.schemas.intent import APIResponseSchema, IntentExtractionSchema

logger = logging.getLogger(__name__)

# Highly optimized system prompt matrix for Roman Urdu parsing
SYSTEM_PROMPT = """You are a highly specialized AI orchestration agent designed to parse mixed-language user requests (especially Roman Urdu, English, and local slang) and extract structured intent data.

Your ONLY job is to output a raw JSON object matching the exact schema provided below. 
Do NOT output markdown code blocks (e.g., ```json ... ```), do not add conversational text, and do not explain your reasoning. Just raw JSON.

Schema:
{
  "service_category": "AC Technician" | "Electrician" | "Plumber" | null,
  "location_context": "string or null",
  "time_preference": "string or null",
  "urgency_level": "normal" | "urgent" | "very urgent",
  "confidence_score": float (between 0.0 and 1.0)
}

Extraction Rules:
1. 'service_category': Must strictly map to "AC Technician", "Electrician", or "Plumber". 
   - If the user mentions cooling, AC, air conditioner, map to "AC Technician". 
   - If lights, wiring, power, switchboard, map to "Electrician". 
   - If water, leak, pipe, tap, motor, sink, map to "Plumber". 
   - If ambiguous or unsupported, set to null.
2. 'location_context': Extract any mentioned areas (e.g., "Clifton block 9", "DHA phase 6", "Gulshan", "Johar"). Null if not provided.
3. 'time_preference': Extract timeframe exactly as implied (e.g., "aj sham 5 baje tak" -> "today 5 PM", "kal morning" -> "tomorrow morning"). Null if not provided.
4. 'urgency_level': Classify as "normal", "urgent", or "very urgent" based on keywords like "bohot zaruri", "emergency", "foran". Default is "normal".
5. 'confidence_score': Provide a dynamic confidence score. >0.85 if clear. <0.70 if the service category is vague, missing, unsupported, or if you are guessing (e.g., "I need help with my lights" -> ~0.60 since it could be minor or require an electrician).
"""

class GeminiIntentParser:
    """
    Parser utilizing Google Gemini API for identifying service intent,
    location, time, and urgency from mixed-language queries.
    """
    
    def __init__(self) -> None:
        self.model: Optional[Any] = None
        
        if GENAI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY not found in environment variables. Gemini API calls will fail.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    # Initialize the generative model
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    logger.info("Successfully initialized Gemini API client.")
                except Exception as e:
                    logger.error(f"Failed to configure Gemini API: {str(e)}", exc_info=True)
        else:
            logger.warning("google-generativeai package is not installed.")
        
    def parse_raw_query(self, query: str) -> APIResponseSchema[IntentExtractionSchema]:
        """
        Parses a raw text query into an intent schema via Google Gemini.
        Includes error catching and returns structured APIResponseSchema.
        
        Args:
            query (str): The raw user query.
            
        Returns:
            APIResponseSchema[IntentExtractionSchema]: The unified API response containing parsed data or an error.
        """
        start_time = time.time()
        logger.info(f"GeminiIntentParser received query for parsing: '{query}'")
        
        try:
            if not self.model:
                logger.error("Gemini model not initialized properly.")
                return APIResponseSchema(
                    success=False,
                    error="Gemini model not initialized properly."
                )
                
            prompt = f"{SYSTEM_PROMPT}\n\nUser Query:\n{query}"
            
            logger.info("Executing Google Gemini API live request...")
            
            # Use generation_config to encourage JSON output
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            
            response_text = response.text.strip()
            
            # Safety cleanup in case Gemini still wraps in markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
                
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            response_text = response_text.strip()
            
            exec_time = round(time.time() - start_time, 3)
            logger.info(f"Raw Gemini API call completed in {exec_time}s. Response payload: {response_text}")
            
            parsed_json = json.loads(response_text)
            
            # Validate via Pydantic
            extracted_data = IntentExtractionSchema(**parsed_json)
            logger.info(f"Successfully validated Pydantic extraction schema. Confidence Score: {extracted_data.confidence_score}")
            
            return APIResponseSchema(
                success=True,
                data=extracted_data
            )
            
        except json.JSONDecodeError as je:
            logger.error(f"Failed to decode JSON from Gemini response: {str(je)}", exc_info=True)
            return APIResponseSchema(
                success=False,
                error="Failed to parse JSON response from LLM."
            )
        except ValidationError as ve:
            logger.error(f"Pydantic validation error: {str(ve)}", exc_info=True)
            return APIResponseSchema(
                success=False,
                error="LLM output did not match the expected schema."
            )
        except Exception as e:
            logger.error(f"Error during Gemini API call parsing: {str(e)}", exc_info=True)
            return APIResponseSchema(
                success=False,
                error=f"Failed to process query through Gemini API: {str(e)}"
            )
