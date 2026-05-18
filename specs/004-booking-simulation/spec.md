# Feature Specification: Booking Simulation & Follow-up Automation

**Feature Branch**: `004-booking-simulation`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "Milestone 4: Booking Simulation & Follow-up Automation"

---

## Part 1: Reference Architecture Analysis

- **State-Machine Design**: Employs a deterministic finite-state machine (FSM) pattern for managing booking lifecycles. Standard transitions follow the strict path: `pending` -> `confirmed` -> `en_route` -> `completed` (or `cancelled`).
- **Event-Driven Simulation**: Simulates an event-driven background worker architecture. Utilizes programmatic logic to trigger mock follow-up notifications and cron-style reminder logs mimicking real-world provider dispatch and user updates.

## Part 2: Current Architecture Analysis

- **Integration Protocols**: The booking engine acts as the final atomic transaction sink, digesting the consolidated outputs from:
  - `/api/orchestrate/intent` (context, urgency, time preference)
  - `/api/orchestrate/match` (selected provider ID)
  - `/api/orchestrate/price` (dynamic price breakdown)
- **Simulation Layer**: Captures state-change events and logs them into a localized trace mock layer (simulating a relational database persistence layer) to verify data integrity.
- **Affected Files**:
  - `backend/src/services/booking_service.py` (new state-machine logic)
  - `backend/src/api/orchestrate/booking.py` (new FastAPI router)
  - Existing `backend/main.py` for routing and `backend/src/schemas/` for payload schemas.

## Part 3: Implementation Plan

1. **Schema Definition**: Define `BookingRequestInput` and `BookingSummaryOutput` Pydantic models ensuring strict data structures.
2. **State-Machine Logic**: Construct the `BookingService` that handles initial booking creation (`pending`) and simulates the immediate state transition to `confirmed`. 
3. **Router Wiring**: Build the FastAPI endpoint `/api/orchestrate/book` to invoke the booking lifecycle and wrap the finalized atomic state in the universal `APIResponseSchema`.
4. **Robust Error Handling**: Implement safeguards against double-booking (simulated by checking an in-memory/mock state lock), invalid provider assignments, and graceful state-validation fallbacks to guarantee 0 crashes.

## Part 4: Implementation Checklist

- Define `BookingRequestInput` schema (user context, provider_id, scheduled_time, dynamic_price object).
- Define `BookingSummaryOutput` schema (booking_id, provider_id, scheduled_time, net_total, current_status).
- Scaffold Pytest edge-case scenario tests outlining handling for concurrent scheduling conflicts and invalid state transitions.

## Constraints

- **Determinism**: All booking transitions, mock notifications, and FSM engines MUST remain entirely deterministic, compiled strictly in pure Python.
- **Isolation**: The workflow must be completely detached from generative LLM prompt blocks. The LLM only interprets text; the backend orchestrates the state securely.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Standard Booking Confirmation (Priority: P1)

A user confirms an AI-orchestrated job request and finalizes the booking for a matched provider.

**Why this priority**: Validates the core "happy path" atomic transaction bringing together intent, matching, and pricing into a finalized state.

**Independent Test**: Can be tested by sending a valid `BookingRequestInput` and verifying the response yields a `confirmed` status with a newly generated `booking_id`.

**Acceptance Scenarios**:
1. **Given** a valid booking payload with an available provider, **When** processed by the booking engine, **Then** the engine generates a unique ID, transitions the state from `pending` to `confirmed`, and logs a mock dispatch notification.

### User Story 2 - Double-Booking Conflict Prevention (Priority: P2)

Two identical scheduling requests for the exact same provider and time slot occur simultaneously.

**Why this priority**: Validates the defensive integrity of the booking layer against race conditions or double-booking.

**Independent Test**: Simulate an in-memory double-booking fault by sending the exact same provider/time payload twice.

**Acceptance Scenarios**:
1. **Given** a provider is already booked for a specific slot, **When** a new request attempts to book that slot, **Then** the system traps the conflict and returns an HTTP 200 `APIResponseSchema` with `success=False` and a structured error indicating provider unavailability.

---

## Edge Cases

- **Invalid State Transition**: What happens if a request tries to transition a `completed` booking to `cancelled`? (The FSM must reject it and return a state-violation error).
- **Missing Required Context**: What if the pricing payload or provider ID is missing? (Fails Pydantic validation cleanly).
- **Provider Not Found**: What if a stale provider ID is submitted? (Returns a graceful `success=False` error rather than a DB crash).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST transition booking states deterministically via FSM rules.
- **FR-002**: System MUST reject double-bookings for the same provider time slot natively.
- **FR-003**: System MUST generate a unique, traceable `booking_id` for every successful request.
- **FR-004**: System MUST log mock notification events synchronously during state transitions.
- **FR-005**: All output MUST be wrapped in the universal `APIResponseSchema`.

### Key Entities

- **BookingRequestInput**: Merged payload of user details, selected provider ID, agreed price, and time context.
- **BookingSummaryOutput**: Finalized atomic record containing `booking_id` and the current FSM state (e.g., `confirmed`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The booking engine processes and transitions states deterministically in under 50ms.
- **SC-002**: The system successfully intercepts 100% of simulated double-booking attempts.
- **SC-003**: 100% of generated responses strictly adhere to the `APIResponseSchema` contract.
