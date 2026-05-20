# Antigravity Trace: 01. Intent Parsing

**Workplan:**
The user has submitted a highly noisy, mixed-language string (Roman Urdu + English). The Intent Agent must invoke the Google GenAI (Gemini-2.5-Flash) LLM to parse the string into a strict `IntentExtractionSchema`.

## Agent Observations
- **User Query:** "ac kharab hai bhaiyya sadar me, sasta wala chahye, female ho"
- **Language Detected:** Roman Urdu

## Reasoning
The query contains service keywords ("ac kharab"), location ("sadar"), constraints ("sasta wala"), and preferences ("female ho"). The agent recognizes the need to map "ac kharab" to the strict `AC Technician` category and extract the remaining PII securely.

## Decisions
- Invoke Gemini API with `SYSTEM_PROMPT`.
- Map output to `IntentExtractionSchema`.
- Validate required slots (Service Category, Location).

## Tool Calls
- `gemini_parser.py -> GeminiIntentParser._call_gemini_api()`

## Action Execution
**API Payload (Extracted JSON):**
```json
{
  "service_category": "AC Technician",
  "location_context": "sadar",
  "time_preference": null,
  "urgency_level": "normal",
  "constraints": "sasta wala",
  "preferences": "female ho",
  "confidence_score": 0.95
}
```

## Error Recovery
None required. The LLM parsed the data with 0.95 confidence. No `SlotFillingError` fallback was triggered.

## Final Outcomes
The raw user string was successfully structured into Pydantic schema format. The orchestration pipeline transitions the state to the Provider Matching Agent.
