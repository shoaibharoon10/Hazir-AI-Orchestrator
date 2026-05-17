# Tasks: Intent Parsing Agent

**Input**: Design documents from `/specs/001-intent-parsing-spec/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Integration tests are explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume web app structure.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create FastAPI router skeleton at `backend/src/api/orchestrate/intent.py`
- [x] T002 [P] Create `backend/src/schemas/intent.py` for Pydantic models
- [x] T003 [P] Create `backend/src/nlp_helpers/gemini_parser.py` for Gemini API integration
- [x] T004 [P] Create `backend/src/lib/fallback_strategies.py` for fail-safe fallback handling

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Implement initial Pydantic `IntentExtractionSchema` in `backend/src/schemas/intent.py` (depends on T002)
- [ ] T006 Implement base FastAPI endpoint in `backend/src/api/orchestrate/intent.py` using `IntentExtractionSchema` (depends on T001, T005)
- [ ] T007 Implement basic Gemini API call in `backend/src/nlp_helpers/gemini_parser.py` (depends on T003)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Extract Service Intent (Priority: P1) 🎯 MVP

**Goal**: A user provides a mixed-language (e.g., Roman Urdu) request, and the Intent Parsing Agent accurately identifies the service category, location, time, and urgency.

**Independent Test**: Can be fully tested by sending a user query to `/api/orchestrate/intent` and verifying the structured output matches the expected service intent and other parameters.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T008 [P] [US1] Create integration test boilerplate for Acceptance Scenario 1 in `backend/tests/integration/test_intent_parsing.py` (depends on T006, T007)
- [ ] T009 [P] [US1] Create integration test boilerplate for Acceptance Scenario 2 in `backend/tests/integration/test_intent_parsing.py` (depends on T006, T007)

### Implementation for User Story 1

- [ ] T010 [US1] Refine `IntentExtractionSchema` to include `service_category`, `location_context`, `time_preference`, `urgency_level`, and `confidence_score` in `backend/src/schemas/intent.py` (depends on T005)
- [ ] T011 [US1] Implement prompt template matrix for Roman Urdu extraction in `backend/src/nlp_helpers/gemini_parser.py` (depends on T007, T010)
- [ ] T012 [US1] Integrate Gemini API parsing logic into FastAPI endpoint in `backend/src/api/orchestrate/intent.py` (depends on T006, T011)
- [ ] T013 [US1] Add logging for User Story 1 operations in `backend/src/api/orchestrate/intent.py` and `backend/src/nlp_helpers/gemini_parser.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Handle Low Confidence (Priority: P1)

**Goal**: When the Intent Parsing Agent's confidence in parsing a user request falls below a threshold (0.70), it stops execution and asks a single clarifying question.

**Independent Test**: Can be fully tested by sending an ambiguous user query to `/api/orchestrate/intent` that triggers low confidence, and verifying the response contains exactly one clarifying question.

### Tests for User Story 2 ⚠️

- [ ] T014 [P] [US2] Create integration test boilerplate for Acceptance Scenario (low confidence) in `backend/tests/integration/test_intent_parsing.py` (depends on T006, T007)

### Implementation for User Story 2

- [ ] T015 [US2] Implement Low-Confidence Gate (< 0.70) in `backend/src/api/orchestrate/intent.py` (depends on T012)
- [ ] T016 [US2] Implement logic to return exactly one clarification question on low confidence in `backend/src/api/orchestrate/intent.py` (depends on T015)
- [ ] T017 [US2] Add logging for User Story 2 operations in `backend/src/api/orchestrate/intent.py` and `backend/src/lib/fallback_strategies.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T018 Code cleanup and refactoring in `backend/src/`
- [ ] T019 Performance optimization of parsing logic in `backend/src/nlp_helpers/gemini_parser.py`
- [ ] T020 Run acceptance tests from `quickstart.md` (if available)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- Tasks T002, T003, T004 in Phase 1 can run in parallel.
- Tasks T008, T009 in Phase 3 can run in parallel.
- Task T014 in Phase 4 can run in parallel.
- User Story 1 and User Story 2 can be worked on in parallel by different team members after Foundational Phase 2 is complete.

---

## Parallel Example: Phase 1 & User Story 1

```bash
# Launch parallel setup tasks:
Task: "Create `backend/src/schemas/intent.py` for Pydantic models"
Task: "Create `backend/src/nlp_helpers/gemini_parser.py` for Gemini API integration"
Task: "Create `backend/src/lib/fallback_strategies.py` for fail-safe fallback handling"

# Launch all tests for User Story 1 together:
Task: "Create integration test boilerplate for Acceptance Scenario 1 in `backend/tests/integration/test_intent_parsing.py`"
Task: "Create integration test boilerplate for Acceptance Scenario 2 in `backend/tests/integration/test_intent_parsing.py`"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
