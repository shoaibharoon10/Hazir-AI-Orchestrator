# Implementation Tasks: Booking Simulation & Follow-up Automation

This checklist outlines the sequential implementation plan for the 004-booking-simulation feature branch.

## Phase 1: Booking Schema Scaffolding

**Goal**: Define Pydantic structures for BookingRequestInput and BookingSummaryOutput.

- [ ] T001 Define `BookingRequestInput` schema in `backend/src/schemas/booking.py`
- [ ] T002 Define `BookingSummaryOutput` schema in `backend/src/schemas/booking.py`

## Phase 2: Finite State Machine Logic

**Goal**: Implement deterministic transitions for pending -> confirmed -> en_route -> completed in pure Python.

- [ ] T003 [US1] Scaffold `BookingService` base class and FSM state variables in `backend/src/services/booking_service.py`
- [ ] T004 [US1] Implement valid state transition logic (pending -> confirmed -> en_route -> completed) in `backend/src/services/booking_service.py`
- [ ] T005 [US2] Implement deterministic double-booking prevention matrix (in-memory lock checking) in `backend/src/services/booking_service.py`
- [ ] T006 [US1] Implement simulated follow-up notification event logging on state transitions in `backend/src/services/booking_service.py`

## Phase 3: Integration Tests Blueprint

**Goal**: Pytest client setups evaluating concurrency blocks, double-booking prevention, and state mutations.

- [ ] T007 [P] [US1] Create Pytest scaffolding in `backend/tests/integration/test_booking.py`
- [ ] T008 [US1] Implement Acceptance Scenario testing standard booking confirmation and ID generation in `backend/tests/integration/test_booking.py`
- [ ] T009 [US2] Implement Acceptance Scenario testing deterministic double-booking rejection in `backend/tests/integration/test_booking.py`

## Phase 4: Endpoint Wiring

**Goal**: Mount the booking system to the FastAPI router with universal APIResponseSchema wrapper.

- [ ] T010 [US1] Create FastAPI router endpoint `/api/orchestrate/book` in `backend/src/api/orchestrate/booking.py`
- [ ] T011 [US1] Connect `BookingService` execution to the `/api/orchestrate/book` route with graceful state-conflict error trapping in `backend/src/api/orchestrate/booking.py`
- [ ] T012 [US1] Register booking router inside the primary application entrypoint in `backend/main.py`

## Phase N: Polish & Cross-Cutting Concerns

**Goal**: Execution timing logging telemetry and Git check-in automation.

- [ ] T013 Implement execution time logging (in ms) inside `backend/src/api/orchestrate/booking.py`
- [ ] T014 Perform final automated Git Check-in and mark User Story completions in `specs/004-booking-simulation/tasks.md`
