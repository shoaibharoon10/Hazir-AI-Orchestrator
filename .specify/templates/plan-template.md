# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

*   **1.1 AI-First System Design**: The proposed solution prioritizes AI orchestration and reasoning over traditional CRUD approaches.
*   **1.2 Spec-Driven Development**: The feature has an approved specification.
*   **1.3 Mobile-First Experience**: The design is optimized for mobile responsiveness and usability on Android/Expo React Native.
*   **1.4 Explainable AI Governance**: All AI-driven decisions include reasoning traces, ranking calculations, confidence scores, fallback logic, workflow transitions, and rejection explanations. Traces are persisted to `agentTraces`.
*   **1.5 Simulation Before Real Dependency**: Development and demonstrations prioritize simulation-safe workflows and mock datasets. Synthetic datasets include `isSynthetic: true`.
*   **2.1 Multi-Agent Orchestration Architecture**: The system uses structured multi-agent orchestration with isolated responsibilities, explicit interfaces, and structured outputs.
*   **2.2 Strict Separation of Responsibilities**: Frontend UI is strictly separated from orchestration, AI reasoning, ranking, backend APIs, and database access.
*   **2.3 API-Centric System Design**: All operations are exposed through backend APIs with consistent `{"success": true, "data": {}, "error": null}` response structures.
*   **2.4 State Machine Enforcement**: Workflows operate through explicit state transitions, with mandatory booking/dispute lifecycles, timestamps, timeline appends, and triggering agent/reasoning context.
*   **2.5 Fallback-First Engineering**: Critical workflows define fallback behaviors.
*   **3.1 Frontend Stack**: Adheres to React Native, Expo, TypeScript, Expo EAS Build, strict TypeScript, and mobile-first UI.
*   **3.2 Backend Stack**: Adheres to Python 3.12+, FastAPI, Pydantic, async-first architecture, typed functions, non-blocking AI calls, and business logic outside route handlers.
*   **3.3 AI & Orchestration Stack**: Adheres to Google Gemini API, Google Antigravity, agent output validation, no direct LLM-to-Firestore writes, and deterministic prompt execution.
*   **3.4 Database & Storage Constraints**: Adheres to Firebase Firestore, Firebase Authentication, backend-validated writes, and logical collection segmentation.
*   **3.5 Maps & Geolocation**: Utilizes Google Places/Geocoding/Distance Matrix APIs with local approximation fallback.
*   **4.1 Explainable Ranking**: Provider recommendations include final score, confidence, ranking explanation, rejection reasons, pricing justification, and availability reasoning.
*   **4.2 Immutable Ranking Formula**: Standardized weighted formula is used; no sole reliance on distance/price/ratings.
*   **4.3 Multilingual Parsing Rules**: Supports English, Urdu, Roman Urdu, and mixed-language prompts with confidence handling.
*   **4.4 Output Validation Requirements**: AI-generated outputs are validated against invalid schedules, overlapping bookings, malformed prices, etc.
*   **5.1 Modular Engineering**: Features are isolated modules with no cross-module internal imports, explicit shared utilities, and reusable business logic.
*   **5.2 Function Standards**: Functions are under 50 lines, public functions/classes have docstrings, strong typing is used, and `Any` is avoided.
*   **5.3 Testing Requirements**: Core orchestration, ranking, workflow state transitions, and critical utilities are tested. Test-first is preferred.
*   **5.4 Logging & Observability**: Logs workflow transitions, agent execution traces, fallback activations, API/validation failures; never logs secrets/tokens/private payloads.
*   **6.1 Secret Management**: All secrets use `.env`, secure environment variables, or protected runtime config; no hardcoded credentials.
*   **6.2 Input Validation**: API boundaries use strict Pydantic validation; no unvalidated payloads trigger workflows/agents/Firestore writes.
*   **6.3 Auditability**: State-changing operations generate audit metadata, timestamps, actor identity, and triggering agent reference.
*   **7.1 Clarification Rule**: Ambiguous specifications lead to one focused clarification question; no assumptions for critical workflows.
*   **7.2 Architectural Decision Rule**: Major architectural decisions propose multiple approaches, explain tradeoffs, and await consent.
*   **7.3 Commit Convention**: Follows `type(scope): description`.
*   **7.4 Constitution Enforcement**: Violations are flagged, documented, and corrected.
*   **8. Mandatory Demo Requirements**: The prototype demonstrates all listed requirements.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
