# Implementation Plan: Intent Parsing Agent

**Branch**: `001-intent-parsing-spec` | **Date**: 2026-05-17 | **Spec**: specs/001-intent-parsing-spec/spec.md
**Input**: Feature specification from `/specs/001-intent-parsing-spec/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement the Intent Parsing Agent to extract service category, location, time, and urgency from mixed-language user requests using Google Gemini API, with a strict low-confidence gate and robust fallback handling.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: FastAPI, Pydantic, Google Gemini API, Google Antigravity (for orchestration)  
**Storage**: N/A  
**Testing**: `pytest` for unit and integration tests. Integration tests will simulate Acceptance Test 1 and Acceptance Test 2 scenarios.  
**Target Platform**: Linux server (FastAPI backend)  
**Project Type**: Backend service  
**Performance Goals**: Validation latency profile check under 1.5 seconds per parse sequence.  
**Constraints**: Low-Confidence Gate: if confidence < 0.70, stop execution and ask exactly ONE clarifying question. No business sorting or ranking logic within this parsing node.  
**Scale/Scope**: Handles all incoming user requests for intent parsing, supporting multiple languages.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

*   **1.1 AI-First System Design**: PASS. The Intent Parsing Agent is a core AI orchestration component.
*   **1.2 Spec-Driven Development**: PASS. A comprehensive spec (`specs/001-intent-parsing-spec/spec.md`) has been created.
*   **1.3 Mobile-First Experience**: N/A (Backend service).
*   **1.4 Explainable AI Governance**: PASS. The agent will expose confidence scores and fallback logic, aligning with the "Low-Confidence Gate" rule. Reasoning traces will be persisted as per requirement.
*   **1.5 Simulation Before Real Dependency**: PASS. Integration tests will simulate scenarios.
*   **2.1 Multi-Agent Orchestration Architecture**: PASS. This agent is explicitly listed as one of the core orchestration agents.
*   **2.2 Strict Separation of Responsibilities**: PASS. This agent focuses solely on parsing intent, not UI, ranking, or database access.
*   **2.3 API-Centric System Design**: PASS. The agent exposes its functionality via a FastAPI endpoint `/api/orchestrate/intent` and will adhere to the specified JSON response structure.
*   **2.4 State Machine Enforcement**: N/A (This agent is a stateless parsing service).
*   **2.5 Fallback-First Engineering**: PASS. Fail-safe fallback strategies are explicitly required for corrupted inputs and API timeouts. Confidence < 0.70 will trigger a clarification question.
*   **3.1 Frontend Stack**: N/A (Backend service).
*   **3.2 Backend Stack**: PASS. Python 3.12+, FastAPI, Pydantic, async-first architecture will be used.
*   **3.3 AI & Orchestration Stack**: PASS. Google Gemini API will be used. Agent outputs will be validated.
*   **3.4 Database & Storage Constraints**: N/A (Direct database interaction is not part of this agent's responsibility).
*   **3.5 Maps & Geolocation**: N/A (Not directly used by this agent, though location context is extracted).
*   **4.1 Explainable Ranking**: N/A (No ranking logic in this agent).
*   **4.2 Immutable Ranking Formula**: N/A (No ranking logic in this agent).
*   **4.3 Multilingual Parsing Rules**: PASS. Explicitly required to support English, Urdu, Roman Urdu, and mixed-language prompts with confidence handling. The Low-Confidence Gate is enforced.
*   **4.4 Output Validation Requirements**: PASS. AI-generated outputs (IntentExtractionSchema) will be validated.
*   **5.1 Modular Engineering**: PASS. The agent will be an isolated module.
*   **5.2 Function Standards**: PASS. Functions will adhere to line limits, docstrings, and strong typing.
*   **5.3 Testing Requirements**: PASS. Integration tests for core orchestration (parsing) and critical utilities will be implemented.
*   **5.4 Logging & Observability**: PASS. Agent execution traces, fallback activations, API/validation failures will be logged.
*   **6.1 Secret Management**: PASS. API keys for Gemini will use `.env` or secure environment variables.
*   **6.2 Input Validation**: PASS. FastAPI with Pydantic will provide strict input validation.
*   **6.3 Auditability**: N/A (This agent is a stateless parsing service. Auditability will be handled at the orchestration layer consuming its output).
*   **7.1 Clarification Rule**: PASS. The Low-Confidence Gate enforces asking a single clarification question.
*   **7.2 Architectural Decision Rule**: PASS. This plan details multiple options for prompt matrices and fallback strategies.
*   **7.3 Commit Convention**: PASS. Will follow `type(scope): description`.
*   **7.4 Constitution Enforcement**: PASS. All relevant rules are flagged and adhered to.
*   **8. Mandatory Demo Requirements**: PASS. Multilingual intent parsing and fallback execution scenarios will be demonstrated.

## Project Structure

### Documentation (this feature)

```text
specs/001-intent-parsing-spec/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── orchestrate/
│   │       └── intent.py  # FastAPI router endpoint for /api/orchestrate/intent
│   ├── nlp_helpers/
│   │   └── gemini_parser.py # Logic for interacting with Google Gemini API
│   ├── schemas/
│   │   └── intent.py  # Pydantic models (IntentExtractionSchema)
│   └── lib/
│       └── fallback_strategies.py # Fail-safe fallback handling logic
└── tests/
    ├── contract/
    ├── integration/
    │   └── test_intent_parsing.py # Integration tests simulating Acceptance Test 1 and 2
    └── unit/
```

**Structure Decision**: The `Option 2: Web application (when "frontend" + "backend" detected)` is chosen as the base. The `backend/src/api/orchestrate/intent.py` will house the FastAPI router, `backend/src/nlp_helpers/gemini_parser.py` will contain the Gemini API integration, and `backend/src/schemas/intent.py` will define the Pydantic models. Fallback strategies will be in `backend/src/lib/fallback_strategies.py`.