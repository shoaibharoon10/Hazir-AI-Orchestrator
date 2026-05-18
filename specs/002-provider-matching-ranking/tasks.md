# Implementation Tasks: Provider Matching & Ranking Engine

This checklist outlines the sequential implementation plan for the 002-provider-matching-ranking feature branch, adhering strictly to the architecture specifications and deterministic constraints.

## Phase 1: Setup & Data Verification Scaffolding

**Goal**: Prepare the foundational schemas and project scaffolding required to handle the 6-factor matching input/output logic securely.

- [ ] T001 Define `MatchingRequestSchema` and `RankedProviderResponseSchema` in `backend/src/schemas/provider.py`
- [ ] T002 Scaffold the `ProviderMatchingEngine` base class in `backend/src/lib/matching_engine.py`

## Phase 2: Core Algorithmic Engineering

**Goal**: Implement the deterministic 6-factor scoring formulas completely decoupled from the LLM routing.

- [ ] T003 [US1] Implement Haversine Formula geospatial distance calculation function in `backend/src/lib/matching_engine.py`
- [ ] T004 [US1] Implement time-window intersection matching logic in `backend/src/lib/matching_engine.py`
- [ ] T005 [US1] Implement composite scoring function integrating global ratings, review recency, and reliability metrics in `backend/src/lib/matching_engine.py`
- [ ] T006 [US1] Implement specific technical skill mapping filter in `backend/src/lib/matching_engine.py`

## Phase 3: Integration Tests Boilerplate

**Goal**: Validate tie-breaking scenarios, geospatial bounds, and exact deterministic sorting.

- [ ] T007 [P] [US1] Create Pytest scaffolding in `backend/tests/integration/test_matching_engine.py`
- [ ] T008 [US1] Implement Acceptance Scenario 1 testing Haversine proximity and scoring ties in `backend/tests/integration/test_matching_engine.py`
- [ ] T009 [US2] Implement Acceptance Scenario 2 testing 'No Providers Available' 0-match fallback in `backend/tests/integration/test_matching_engine.py`

## Phase 4: Endpoint Wiring

**Goal**: Connect the deterministic engine to the active FastAPI ecosystem.

- [ ] T010 [US1] Create FastAPI router endpoints in `backend/src/api/orchestrate/matching.py`
- [ ] T011 [US1] Connect `ProviderMatchingEngine` instance to the `/api/orchestrate/match` route in `backend/src/api/orchestrate/matching.py`
- [ ] T012 [US2] Integrate `/api/orchestrate/match` fallback strategies to return structured 0-match arrays safely without HTTP 500 crashes.

## Phase N: Polish & Cross-Cutting Concerns

**Goal**: Traceability, runtime optimization, and automated snapshotting.

- [ ] T013 Implement execution time logging and performance tracing in `backend/src/api/orchestrate/matching.py`
- [ ] T014 Polish logger outputs with tie-breaking warnings in `backend/src/lib/matching_engine.py`
- [ ] T015 Perform final automated Git Check-in automation and finalize User Story completions.
