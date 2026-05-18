# Implementation Tasks: Unified Master Workflow Validation

This checklist outlines the sequential implementation plan for the 005-unified-orchestration feature branch.

## Phase 1: Master Schema Scaffolding

**Goal**: Define Pydantic models for UnifiedOrchestratorInput accepting a raw query string, and UnifiedOrchestratorOutput returning the combined end-to-end execution breakdown.

- [x] T001 Define `UnifiedOrchestratorInput` schema in `backend/src/schemas/unified.py`
- [x] T002 Define `UnifiedOrchestratorOutput` schema in `backend/src/schemas/unified.py`

## Phase 2: Master Controller Facade Engineering

**Goal**: Implement the sequential pipeline manager that calls Intent, Match, Price, and Book services independently and passes tokens cleanly in pure Python.

- [x] T003 [US1] Scaffold `UnifiedOrchestratorService` in `backend/src/services/unified_service.py`
- [x] T004 [US1] Implement atomic sequence mapping: Intent Extraction -> Provider Matching -> Price Calculation -> Booking inside `backend/src/services/unified_service.py`
- [x] T005 [US2] Implement composite rollback handlers wrapping 0-match results and downstream FSM exceptions safely in pure Python without crashing the backend.

## Phase 3: Global E2E Integration Tests

**Goal**: Pytest suite testing the holistic `/api/orchestrate/run-all` endpoint with raw Roman Urdu strings, validating successful downstream data flow.

- [x] T006 [P] [US1] Create Pytest scaffolding in `backend/tests/e2e/test_unified_workflow.py`
- [x] T007 [US1] Implement Acceptance Scenario testing successful raw text query to confirmed booking flow in `backend/tests/e2e/test_unified_workflow.py`
- [x] T008 [US2] Implement Acceptance Scenario testing graceful downstream aborts (e.g., zero providers matched) in `backend/tests/e2e/test_unified_workflow.py`

## Phase 4: Endpoint Wiring & Global Mount

**Goal**: Expose the master POST router path at `/api/orchestrate/run-all` inside backend/main.py.

- [x] T009 [US1] Create FastAPI router endpoint `/api/orchestrate/run-all` in `backend/src/api/orchestrate/unified.py`
- [x] T010 [US1] Register unified router inside the primary application entrypoint in `backend/main.py`

## Phase N: Polish & Cross-Cutting Concerns

**Goal**: Final Polish, compiling total millisecond pipeline metrics logging, and Git automation check-in.

- [ ] T011 Implement E2E execution time logging (in ms) inside `backend/src/api/orchestrate/unified.py`
- [ ] T012 Perform final automated Git Check-in and mark User Story completions in `specs/005-unified-orchestration/tasks.md`
