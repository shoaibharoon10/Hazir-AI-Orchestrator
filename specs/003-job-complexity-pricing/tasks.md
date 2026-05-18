# Implementation Tasks: Job Complexity & Dynamic Pricing Engine

This checklist outlines the sequential implementation plan for the 003-job-complexity-pricing feature branch.

## Phase 1: Schema Scaffolding & Input Verification

**Goal**: Define Pydantic structures for PricingRequestInput and PriceBreakdownOutput.

- [ ] T001 Define `PricingRequestInput` schema in `backend/src/schemas/pricing.py`
- [ ] T002 Define `PriceBreakdownOutput` schema in `backend/src/schemas/pricing.py`

## Phase 2: Core Algorithmic Pricing Engineering

**Goal**: Implement rule-based complexity tier matrices, surge multipliers overflow ceiling, distance buffers, and loyalty discounts.

- [ ] T003 [US1] Scaffold `PricingService` base class in `backend/src/services/pricing_service.py`
- [ ] T004 [US1] Implement rule-based complexity evaluation matrix (Basic, Intermediate, Complex) in `backend/src/services/pricing_service.py`
- [ ] T005 [US2] Implement dynamic surge multiplier calculation with hard-cap overflow ceiling in `backend/src/services/pricing_service.py`
- [ ] T006 [US1] Implement geospatial distance buffer cost calculation handling 0km boundary natively in `backend/src/services/pricing_service.py`
- [ ] T007 [US1] Implement historical loyalty tier discount logic in `backend/src/services/pricing_service.py`
- [ ] T008 [US2] Implement composite `calculate_net_total` logic enforcing 2-decimal rounding strictness in `backend/src/services/pricing_service.py`

## Phase 3: Integration Tests Setup

**Goal**: Pytest scaffolding for edge cases like zero-distance validation, max surge cap, and decimal rounding.

- [ ] T009 [P] [US1] Create Pytest scaffolding in `backend/tests/integration/test_pricing_engine.py`
- [ ] T010 [US1] Implement Acceptance Scenario testing Basic Flat-Rate Computation without surge overrides in `backend/tests/integration/test_pricing_engine.py`
- [ ] T011 [US2] Implement Acceptance Scenario testing Complex Job with Urgent Surge tracking max caps and precision floats in `backend/tests/integration/test_pricing_engine.py`

## Phase 4: Endpoint Wiring

**Goal**: Mount the service engine to the FastAPI router with universal APIResponseSchema wrapper.

- [ ] T012 [US1] Create FastAPI router endpoint `/api/orchestrate/price` in `backend/src/api/orchestrate/pricing.py`
- [ ] T013 [US1] Connect `PricingService` execution to the `/api/orchestrate/price` route with graceful fallback error trapping in `backend/src/api/orchestrate/pricing.py`
- [ ] T014 [US1] Register pricing router inside the primary application entrypoint in `backend/main.py`

## Phase N: Polish & Cross-Cutting Concerns

**Goal**: Execution timing metrics logging and Git automation.

- [ ] T015 Implement execution time logging (in ms) inside `backend/src/api/orchestrate/pricing.py`
- [ ] T016 Perform final automated Git Check-in and mark User Story completions in `specs/003-job-complexity-pricing/tasks.md`
