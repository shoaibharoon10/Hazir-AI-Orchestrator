# Feature Specification: Intent Parsing Agent

**Feature Branch**: `001-intent-parsing-spec`
**Created**: 2026-05-17
**Status**: Draft
**Input**: User description: "Create a comprehensive Technical Specification for the "Intent Parsing Agent" inside the `.spec/` directory, following the exact structural template from the book.## Part 1: Reference Architecture Analysis- Conversational NLP token extraction and intent parsing architectures using LLMs (specifically Google Gemini API).- Handling of mixed-language text data (code-switching, Roman Urdu, slang, phonetics) and common pitfalls in traditional rule-based regex parsing.- Best practices for dynamic confidence scoring models in Agentic AI.## Part 2: Current Architecture Analysis- Constraints imposed by Project Constitution v3.1 regarding the Low-Confidence Gate (Hard Rule: if confidence < 0.70, stop execution and ask exactly ONE clarifying question).- Extraction targets required by Challenge 2: service category (AC Technician, Electrician, Plumber), location context, time preference, and urgency level.- Affected files: backend API routes, NLP helper modules, and intent schemas.

## Part 3: Implementation Plan
- Phased approach for creating the translation/parsing prompt matrices and building the FastAPI router endpoint `/api/orchestrate/intent`.
- Fail-safe strategy for fallback handling when handling highly corrupted inputs or Groq/Gemini API timeouts.

## Part 4: Implementation Checklist
- Pydantic models for the structured Intent Output (`IntentExtractionSchema`).
- System prompt design block specialized for Roman Urdu context routing.
- Integration tests simulating Acceptance Test 1 and Acceptance Test 2 scenarios.

## Constraints
- Explicit boundaries: The Intent Agent must NEVER guess or hallucinate components if confidence is below 0.70.
- No business sorting or ranking logic may exist inside this parsing node.

## Success Criteria
- Deterministic extraction outputs mapping directly to Type A dataset categories with structured error shape responses.
- Validation latency profile check under 1.5 seconds per parse sequence."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract Service Intent (Priority: P1)

A user provides a mixed-language (e.g., Roman Urdu) request, and the Intent Parsing Agent accurately identifies the service category, location, time, and urgency.

**Why this priority**: This is the core functionality and directly enables the agent to orchestrate services.

**Independent Test**: Can be fully tested by sending a user query to `/api/orchestrate/intent` and verifying the structured output matches the expected service intent and other parameters.

**Acceptance Scenarios**:

1.  **Given** a Roman Urdu request like "mujhe ac theek karwana hai Clifton block 9 me aj sham 5 baje tak, bohot zaruri hai" (I need to get AC fixed in Clifton block 9 today by 5 PM, very urgent), **When** the Intent Parsing Agent processes it, **Then** it extracts `service_category: "AC Technician"`, `location_context: "Clifton block 9"`, `time_preference: "today 5 PM"`, `urgency_level: "very urgent"` with confidence >= 0.70.
2.  **Given** an English request like "I need an electrician for Defence Phase 6 tomorrow morning", **When** the Intent Parsing Agent processes it, **Then** it extracts `service_category: "Electrician"`, `location_context: "Defence Phase 6"`, `time_preference: "tomorrow morning"`, `urgency_level: "normal"` with confidence >= 0.70.

---

### User Story 2 - Handle Low Confidence (Priority: P1)

When the Intent Parsing Agent's confidence in parsing a user request falls below a threshold (0.70), it stops execution and asks a single clarifying question.

**Why this priority**: This is a critical constraint from Project Constitution v3.1, ensuring robust error handling and preventing hallucinations.

**Independent Test**: Can be fully tested by sending an ambiguous user query to `/api/orchestrate/intent` that triggers low confidence, and verifying the response contains exactly one clarifying question.

**Acceptance Scenarios**:

1.  **Given** an ambiguous request like "I need help with my lights", **When** the Intent Parsing Agent processes it and its confidence is < 0.70, **Then** it returns an error response with exactly one clarifying question (e.g., "Are you looking for an electrician or something else?") and stops further execution.

---

### Edge Cases

-   What happens when the input is highly corrupted or contains extreme slang/phonetics? The agent should either parse with high confidence (if possible) or trigger the Low-Confidence Gate.
-   How does the system handle Groq/Gemini API timeouts during parsing? It should trigger a fail-safe fallback strategy as defined in the Implementation Plan.
-   What if the request implies multiple service categories? The agent should extract the most probable primary category or trigger the Low-Confidence Gate if ambiguous.

## Requirements *(mandatory)*

### Functional Requirements

-   **FR-001**: System MUST extract `service category` (AC Technician, Electrician, Plumber), `location context`, `time preference`, and `urgency level` from user requests.
-   **FR-002**: System MUST process mixed-language text data (code-switching, Roman Urdu, slang, phonetics).
-   **FR-003**: System MUST stop execution and ask exactly ONE clarifying question if confidence is below 0.70 (Low-Confidence Gate).
-   **FR-004**: System MUST expose a FastAPI router endpoint at `/api/orchestrate/intent` for intent parsing.
-   **FR-005**: System MUST implement fail-safe fallback handling for highly corrupted inputs or Groq/Gemini API timeouts.
-   **FR-006**: System MUST use Pydantic models for structured intent output (`IntentExtractionSchema`).
-   **FR-007**: System MUST include a system prompt design block specialized for Roman Urdu context routing.
-   **FR-008**: System MUST NOT guess or hallucinate components if confidence is below 0.70.
-   **FR-009**: System MUST NOT include business sorting or ranking logic within this parsing node.

### Key Entities *(include if feature involves data)*

-   **IntentOutput**: Structured output containing `service_category` (string, enum), `location_context` (string), `time_preference` (string), `urgency_level` (string, enum), and `confidence_score` (float).

## Success Criteria *(mandatory)*

### Measurable Outcomes

-   **SC-001**: Deterministic extraction outputs mapping directly to Type A dataset categories with structured error shape responses.
-   **SC-002**: Validation latency profile check under 1.5 seconds per parse sequence.