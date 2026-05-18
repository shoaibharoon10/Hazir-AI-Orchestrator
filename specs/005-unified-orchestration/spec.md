# Feature Specification: Unified Master Workflow Validation

**Feature Branch**: `005-unified-orchestration`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "Milestone 5: Unified Master Workflow Validation"

---

## Part 1: Reference Architecture Analysis

- **Master Controller Pattern**: Implements a highly cohesive facade controller mapping a single entrypoint to the entire sequential pipeline. 
- **Sequential Pipeline Flow**:
  1. **Intent Extraction**: Parses the raw Roman Urdu text string.
  2. **Geospatial Provider Matching**: Matches skills, calculates Haversine distance, and ranks available providers.
  3. **Dynamic Price Calculation**: Determines base tier, applies urgency surge caps, and calculates travel buffers.
  4. **FSM Booking Confirmation**: Locks the slot, simulates worker notifications, and generates the final booking trace.
- **Composite Exception Rollbacks**: Simulates transactional safe fallback closures if any downstream node (e.g., zero providers matched, pricing bounds exceeded) encounters a hard stop.

## Part 2: Current Architecture Analysis

- **Integration Endpoints**: A new master orchestrator route is exposed at `/api/orchestrate/run-all`.
- **System Sink**: This endpoint consolidates the existing schemas (`IntentExtractionSchema`, `MatchingRequestSchema`, `PricingRequestInput`, `BookingRequestInput`) internally. The external client only provides the raw text query and basic user context.
- **Affected Files**:
  - `backend/src/api/orchestrate/unified.py` (new master router)
  - `backend/src/schemas/unified.py` (new schema definitions)
  - Existing schemas and service classes from previous milestones.

## Part 3: Implementation Roadmap

1. **Master Request Schema**: Define `UnifiedRequestInput` taking a raw text string, customer ID, and location context.
2. **Controller Wiring**: Implement the `/run-all` route that sequentially initializes `GeminiIntentParser`, `MatchingService`, `PricingService`, and `BookingService`.
3. **Internal Data Passing**: Map the output of step N as the input payload parameters for step N+1 completely in memory.
4. **Exception Guarding**: Wrap the entire pipeline in an atomic try-except. If intent fails, run regex fallback. If matching yields 0 providers, return a graceful 0-match payload. If booking detects a double-booking, trap it seamlessly and return a structured 400 Bad Request wrapped inside `APIResponseSchema`.

## Part 4: Implementation Checklist (Master Acceptance Tests)

- Define `UnifiedRequestInput` and `UnifiedSummaryOutput` schemas.
- **Global E2E Pytest**: Create `backend/tests/e2e/test_unified_workflow.py` to assert that a complete raw Roman Urdu text string flows flawlessly into a confirmed booking response block.
- **Fallback Assertions**: Assert that an unparseable query routes through regex fallback and still succeeds the pipeline.
- Scaffold the `unified_router` and attach to `main.py`.

## Constraints

- **Determinism**: The entire sequence orchestration logic MUST remain 100% deterministic and written in pure Python. The only LLM interaction occurs strictly inside the isolated Intent Extraction bounds.
- **Atomic Integrity**: If the pipeline fails midway, the response must reflect a clean failure state rather than a 500 stack trace.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - E2E Master Orchestration (Priority: P0)

A user submits a single raw Roman Urdu prompt, and the system autonomously matches a provider, prices the job, and books the slot in one fluid transaction.

**Why this priority**: Validates the ultimate goal of the AI Service Orchestrator, proving that decoupled micro-services can coordinate a single high-level transaction natively.

**Independent Test**: Can be verified natively via Pytest hitting the `/api/orchestrate/run-all` endpoint with a single payload.

**Acceptance Scenarios**:
1. **Given** a raw text string requesting a plumber urgently, **When** processed by the master controller, **Then** the intent is extracted, a top-ranked plumber is matched, urgent surge pricing is calculated, and a confirmed `booking_id` is returned natively.

### User Story 2 - Cascading Failure Graceful Exit (Priority: P1)

A user requests an incredibly rare skill where zero providers exist in the mock database.

**Why this priority**: Validates the resilience of the master controller to abort the transaction cleanly without generating null reference crashes in the pricing or booking phases.

**Independent Test**: Provide an intent query that maps to an unseeded skill category.

**Acceptance Scenarios**:
1. **Given** a validated intent for an unknown skill, **When** the matching engine returns an empty array, **Then** the master controller aborts the pricing and booking phases and immediately returns an `APIResponseSchema` with `success=True` but a `data` block explicitly stating no providers were found, halting the booking FSM cleanly.

---

## Edge Cases

- **Double Booking in E2E**: The chosen top-ranked provider is suddenly booked between the match and book phases. (The master controller traps the `DoubleBookingError` and returns a 400).
- **LLM Rate Limit in E2E**: The Gemini parser fails due to quota exhaustion. (The try-except block falls back to the regex mapper, allowing the master transaction to still succeed natively).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Master controller MUST execute Intent -> Match -> Price -> Book sequentially.
- **FR-002**: Master controller MUST translate data shapes between internal services in-memory natively.
- **FR-003**: Master controller MUST handle all downstream node exceptions using localized exception blocks.
- **FR-004**: System MUST return all data unified inside `APIResponseSchema`.

### Key Entities

- **UnifiedRequestInput**: `query` (string), `customer_id` (string), `user_location` (string).
- **UnifiedSummaryOutput**: Consolidated data map summarizing the intent extracted, provider matched, exact price billed, and the final FSM booking state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Master pipeline executes the entire end-to-end workflow natively in under 300ms (excluding external LLM network latency).
- **SC-002**: System gracefully survives 100% of injected 0-match and double-booking collision faults natively.
