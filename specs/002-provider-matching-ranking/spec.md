# Feature Specification: Provider Matching & Ranking Engine

**Feature Branch**: `002-provider-matching-ranking`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "Develop a Provider Matching & Ranking Engine enforcing a 6-factor deterministic ranking algorithm decoupled from the LLM prompt layer."

---

## Part 1: Reference Architecture Analysis

- **Multi-factor Recommendation System Design**: The matching engine follows a composite scoring pattern. It utilizes Firestore relational simulation querying to batch-fetch candidate providers based on primary index keys (e.g., service category and active status) before performing in-memory secondary filtering and sorting.
- **Geospatial and Temporal Indexing**: 
  - *Geographical Coordinates*: Applies the Haversine Formula algorithm to calculate precise radial distance between the parsed user location and provider service radii.
  - *Real-time Availability*: Intersects the user's requested time window against the provider's active scheduling matrix to ensure strict temporal overlap before applying scores.

## Part 2: Current Architecture Analysis

- **Integration Constraints**: The engine acts as the direct downstream consumer of the `/api/orchestrate/intent` node. It strictly requires the `IntentExtractionSchema` output payload (service_category, location_context, time_preference, urgency_level) to initialize matching parameters.
- **6-Factor Matching Requirement**: Every candidate provider must be evaluated against the official multi-variable formula:
  1. *Distance/Travel Time Calculation*: Inversely proportional weight based on radial proximity.
  2. *Matching Availability Matrix*: Boolean filter that severely penalizes or disqualifies misaligned schedules.
  3. *Global Rating Weights*: Aggregate provider rating out of 5.0.
  4. *Review Recency Scoring*: Score multiplier boosting providers with active, recent positive reviews.
  5. *Historical Reliability*: Penalty metrics based on past no-shows or late arrivals.
  6. *Technical Skill Specialization*: Tag-based matching mapping the specific extracted problem (e.g., "AC cooling") to the provider's explicit expertise tags.
- **Affected Files**:
  - `backend/src/api/orchestrate/matching.py` (new router file)
  - `backend/src/schemas/provider.py` (or existing schemas requiring augmentation for the 6 factors)
  - Existing intent routing layers to pipe output correctly to the matching service.

## Part 3: Implementation Plan

- **Sequential Development**:
  1. **Score Compilation Modules**: Implement isolated mathematical functions for the Haversine distance, availability overlap, and weighted scoring.
  2. **Router Endpoint**: Develop the `/api/orchestrate/match` FastAPI endpoint that orchestrates these sub-modules.
  3. **Integration & Assembly**: Connect the output of the LLM parser natively into this routing endpoint.
- **Robust Fallback Strategy**: 
  - If a "No Providers Available" threshold is hit (e.g., all providers score below an acceptable minimum), the pipeline must gracefully return a structured fallback response wrapped in `APIResponseSchema`, offering alternative time slots or broadened search radii, without throwing HTTP 500 crashes.
  - Mitigate database read latency faults using timeout wrappers and cached generic provider profiles if the main DB hangs.

## Part 4: Implementation Checklist

- **Pydantic Verification Shapes**: Define strict schemas for the `MatchingRequestSchema` (input from the intent node) and `RankedProviderResponseSchema` (output array containing weighted scores and provider details).
- **Strict Test Setup**: 
  - Formulate Pytest scenarios testing Haversine edge cases.
  - Implement Acceptance Scenarios where multiple top-ranked providers tie; test tie-breaking logic (e.g., prioritizing distance over rating).
  - Simulate two providers competing for an overlapping calendar window to verify temporal exclusion sorting.

## Constraints

- **Explicit Limits**: Business ranking logic MUST be entirely deterministic. It must be executed strictly as a backend Python pipeline service. It must be completely decoupled from the Google Gemini LLM prompt layer parameters (the LLM extracts intent; the backend purely calculates math).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find Nearest Available Technician (Priority: P1)

A user urgently requests an AC Technician for "today 5 PM" in "Clifton block 9". The system processes the intent, queries Firestore for active AC Technicians, and returns a ranked list prioritizing proximity and immediate availability.

**Why this priority**: Core value proposition. Fulfills the MVP requirement of connecting a recognized need with a viable, available service provider.

**Independent Test**: Can be fully tested by sending a mocked intent payload to `/api/orchestrate/match` and verifying the response contains an array of providers sorted descending by their composite 6-factor score.

**Acceptance Scenarios**:
1. **Given** a parsed intent for an AC Technician in a specific zone, **When** the matching engine runs, **Then** it returns the top 3 available technicians ordered by highest overall composite score.
2. **Given** an intent requiring urgent service, **When** the matching engine runs, **Then** it heavily weights current availability and proximity over global rating, bumping closer available providers to the top.

### User Story 2 - Handle No Providers Available (Priority: P2)

A user requests an Electrician at 3:00 AM in a remote area where no providers are scheduled or within radius.

**Why this priority**: Essential for UX and error handling. Prevents infinite loading loops or unhandled exceptions.

**Independent Test**: Can be fully tested by requesting an impossible time/location combination and validating the structured fallback response.

**Acceptance Scenarios**:
1. **Given** zero providers match the availability matrix and distance constraint, **When** the scoring algorithm completes, **Then** the endpoint returns a successful `APIResponseSchema` with an empty provider list and a `message` offering alternative time slots.

---

## Edge Cases

- What happens when two providers have the exact same composite score? (Tie-breaker rule required, e.g., default to closest distance or highest total completed jobs).
- How does system handle database read timeouts during the initial bulk provider fetch? (Fallback to cached pool or return graceful failure).
- What happens if the parsed intent contains a `location_context` that cannot be resolved to lat/long coordinates? (Fallback to city-center default or ask for clarification).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate geographical distance using the Haversine Formula based on user and provider coordinate pairs.
- **FR-002**: System MUST apply all 6 factors in the weighted scoring algorithm deterministically.
- **FR-003**: System MUST expose the matching logic through the `/api/orchestrate/match` endpoint.
- **FR-004**: System MUST accept the output schema of the Intent Parsing Agent as its direct input.
- **FR-005**: System MUST NOT use LLMs to perform the sorting or ranking of providers.

### Key Entities

- **MatchRequest**: The payload containing `service_category`, `location_context`, `time_preference`, and `urgency_level` passed from the intent phase.
- **RankedProvider**: A provider entity augmented with its calculated `composite_score`, `distance_km`, and `matched_skills`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The matching engine algorithm executes and returns ranked results in under 500ms (excluding network latency).
- **SC-002**: 100% of generated provider arrays are strictly sorted in descending order based on the final computed deterministic score.
- **SC-003**: In scenarios with 0 available providers, the system never returns an HTTP 500 error, instead cleanly returning a valid API schema fallback.
