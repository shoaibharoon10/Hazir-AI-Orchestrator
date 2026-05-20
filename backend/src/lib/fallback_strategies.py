import logging
import re
from src.schemas.intent import APIResponseSchema, IntentExtractionSchema

logger = logging.getLogger(__name__)

# Karachi area tokens for location extraction
KARACHI_LOCATIONS = [
    "clifton", "dha", "gulshan", "johar", "nazimabad", "sadar",
    "defence", "north nazimabad", "malir", "korangi", "landhi",
    "gulistan", "liaquatabad", "fb area", "federal b", "shah faisal",
    "bahria town", "scheme 33", "block", "phase"
]

# Time-related tokens (Roman Urdu + English)
TIME_TOKENS = re.compile(
    r'\b('
    r'aaj|kal|parson|subah|dopahar|sham|raat|abhi|foran|'
    r'today|tomorrow|morning|evening|afternoon|night|now|asap|'
    r'\d{1,2}\s*(am|pm|baje|bajay)'
    r')\b',
    re.IGNORECASE
)


def execute_regex_fallback(query: str) -> APIResponseSchema:
    """
    Aggressive Roman Urdu + English regex fallback parser.
    Returns None for any slot not explicitly found in the query string.
    """
    logger.info(f"Executing regex fallback for query: '{query}'")

    q_lower = query.lower()
    category = None

    # Category extraction — Roman Urdu + English hybrid patterns
    if re.search(r'\b(ac|air\s*condition|hvac|cool|thanda|thand)', q_lower):
        category = "AC Technician"
    elif re.search(r'\b(plumb|pani|paani|leak|pipe|tap|nal|nalkay|sink|drain|motor\b)', q_lower):
        category = "Plumber"
    elif re.search(r'\b(electric|bijli|wir|plug|switch|short\s*circuit|light|bulb)', q_lower):
        category = "Electrician"
    elif re.search(r'\b(beaut|salon|parlour|parlor|makeup|facial|mehndi|thread)', q_lower):
        category = "Beautician"
    elif re.search(r'\b(appliance|wash|fridge|freez|microwave|oven|geyser|geezar|machine\s*band)', q_lower):
        category = "Appliance Repair"
    elif re.search(r'\b(tutor|parhana|math|teacher|academy|school|science|english|tuition|parhai)', q_lower):
        category = "Tutor"

    if not category:
        logger.warning("[Fallback] Could not determine service category from query tokens.")
        return APIResponseSchema(
            success=False,
            error="Regex fallback could not determine category from tokens."
        )

    # Location extraction — scan for standard demo locations first, then fall back to others
    location = None
    demo_locations = ["clifton", "johar", "sadar", "dha", "nazimabad", "gulshan"]
    for loc in demo_locations:
        if loc in q_lower:
            location = loc.title()
            break
            
    if not location:
        for loc in KARACHI_LOCATIONS:
            if loc in q_lower:
                location = loc.title()
                break

    # Time extraction — scan for demo times first, then fall back to the regex pattern
    time_pref = None
    demo_times = ["10 am", "urgent", "aaj raat", "kal subha", "now"]
    for dt in demo_times:
        if dt in q_lower:
            time_pref = dt.title()
            break
            
    if not time_pref:
        time_match = TIME_TOKENS.search(query)
        if time_match:
            time_pref = time_match.group(0).strip()

    # Urgency extraction
    urgency = "normal"
    if re.search(r'\b(urgent|foran|bohot\s*zaruri|emergency|abhi|jaldi)', q_lower):
        urgency = "urgent"

    logger.info(
        f"[Fallback] Extracted: category={category}, location={location}, "
        f"time={time_pref}, urgency={urgency}"
    )

    return APIResponseSchema(
        success=True,
        data=IntentExtractionSchema(
            service_category=category,
            location_context=location,
            time_preference=time_pref,
            urgency_level=urgency,
            confidence_score=0.75
        )
    )
