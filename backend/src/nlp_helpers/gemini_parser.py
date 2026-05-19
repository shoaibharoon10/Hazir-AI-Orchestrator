import json
import logging
import os
import time
from typing import Any, Optional

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from pydantic import ValidationError

from src.schemas.intent import APIResponseSchema, IntentExtractionSchema

logger = logging.getLogger(__name__)

# Highly optimized system prompt matrix for Roman Urdu parsing
SYSTEM_PROMPT = """You are an expert multilingual AI orchestration agent fluent in pure Urdu script (اردو), Roman Urdu vernacular, and English. You specialise in parsing mixed-language Pakistani household service requests and extracting structured intent.

Your ONLY job is to output a raw JSON object matching the exact schema provided below.
Do NOT output markdown code blocks, do not add conversational text, and do not explain your reasoning. Just raw JSON.

Schema:
{
  "service_category": "AC Technician" | "Electrician" | "Plumber" | "Beautician" | "Appliance Repair" | null,
  "location_context": "string or null",
  "time_preference": "string or null",
  "urgency_level": "normal" | "urgent" | "very urgent",
  "confidence_score": float (between 0.0 and 1.0)
}

Extraction Rules:
1. 'service_category': Strictly map to exactly one of the five allowed values:
   - "AC Technician": user mentions AC, air conditioner, cooling, hvac, ٹھنڈک, اے سی ٹھیک
   - "Electrician": lights, wiring, power, switch, plug, bijli, بجلی, short circuit
   - "Plumber": water, leak, pipe, tap, motor, drain, پانی, ٹونٹی, nal band
   - "Beautician": salon, makeup, beauty, parlour, facial, mehndi, threading, بیوٹی پارلر, ميک اپ
   - "Appliance Repair": washing machine, fridge, microwave, dishwasher, گیزر, oven, machine band hai
   - If ambiguous or completely unsupported, set to null.
2. 'location_context': Extract any Karachi area (Clifton, DHA, Gulshan, Johar, Nazimabad, Sadar, etc.). Null if not provided.
3. 'time_preference': Extract timeframe as implied ("aaj sham 5 baje" -> "today 5 PM", "kal subah" -> "tomorrow morning"). Null if not mentioned.
4. 'urgency_level': "normal", "urgent", or "very urgent" based on keywords like "bohot zaruri", "فوری", "emergency", "abhi", "foran". Default "normal".
5. 'confidence_score': >0.85 if clear service and location. <0.70 if service category is vague or guessed.
"""

class GeminiIntentParser:
    """
    Parser utilizing Google GenAI SDK for identifying service intent,
    location, time, and urgency from mixed-language queries.
    """
    
    def _initialize_model(self) -> None:
        if not GENAI_AVAILABLE:
            logger.error("google-genai package is not installed.")
            return
            
        # Fix: Check both typical environment variable names
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("Neither GOOGLE_API_KEY nor GEMINI_API_KEY found in environment. Gemini API calls will fail.")
        else:
            try:
                self.client = genai.Client(api_key=api_key)
                self.model_id = 'gemini-2.5-flash'
                logger.info("Successfully initialized Gemini API client.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini API: {str(e)}", exc_info=True)

    def __init__(self) -> None:
        self.client: Optional[Any] = None
        self.model_id: Optional[str] = None
        self._initialize_model()
        
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
            if not self.client:
                # Structural Fix: Lazy load the model in case environment variables were 
                # populated after the module was initially imported by FastAPI
                self._initialize_model()

            if not self.client:
                logger.error("Gemini client not initialized properly.")
                return APIResponseSchema(
                    success=False,
                    error="Gemini client not initialized properly."
                )
                
            prompt = f"{SYSTEM_PROMPT}\n\nUser Query:\n{query}"
            
            logger.info("Executing Google Gemini API live request...")
            
            # Use generation_config to encourage JSON output with robust model routing fallbacks
            response = None
            last_err = None
            models_to_try = [self.model_id, 'gemini-1.5-flash', 'gemini-1.5-pro']
            for m in models_to_try:
                if not m:
                    continue
                try:
                    logger.info(f"Attempting Gemini generation with model: '{m}'")
                    response = self.client.models.generate_content(
                        model=m,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        )
                    )
                    # Dynamically cache successful model for future fast paths
                    self.model_id = m
                    logger.info(f"Successfully processed query using Gemini model: '{m}'")
                    break
                except Exception as exc:
                    logger.warning(f"Gemini call failed with model '{m}': {str(exc)}")
                    last_err = exc

            if not response:
                raise last_err or Exception("All Gemini model routing attempts failed.")
            
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
