# Agent Trace: Intent Parsing
**Agent:** PlannerAgent
**Thought:** Extracting structured intent from multilingual query (Urdu / Roman Urdu / English)
**Action:** Invoked GeminiIntentParser

**Thought:** Gemini NLP parsing complete. Confidence score: 0.75. Missing slot / fallback status: Success.
**Action:** Evaluated NLP Extraction

**Thought:** Concurrently validating 3 mandatory slots: service_category, location_text, scheduled_time
**Action:** Performing Slot-Filling Check

**Thought:** All 3 mandatory slots verified. Handing off to MatchingAgent.
**Action:** Slot Validation Passed
