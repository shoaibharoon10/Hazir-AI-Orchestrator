<!-- Sync Impact Report:
Version change: 0.0.0 (initial) → 1.0.0
Modified principles:
- [Existing principles replaced with new ones]
Added sections: Core Product Philosophy, Architecture Principles, Technology Constraints, AI Governance & Decision Rules, Code Quality Standards, Security & Data Governance, Workflow & Collaboration Rules, Mandatory Demo Requirements
Removed sections: [None explicitly removed, but placeholders are replaced]
Templates requiring updates:
- .specify/templates/plan-template.md ⚠ pending
- .specify/templates/spec-template.md ⚠ pending
- .specify/templates/tasks-template.md ⚠ pending
- .specify/templates/commands/sp.constitution.md ✅ updated
- .specify/templates/commands/sp.phr.md ⚠ pending
Follow-up TODOs: None
-->
# Haazir — AI Service Orchestrator for Informal Economy Constitution

## Core Principles

### 1.1 AI-First System Design
This project must behave as an AI orchestration platform rather than a traditional CRUD marketplace application. Reasoning quality, workflow coordination, explainability, decision transparency, and autonomous execution are prioritized above UI complexity.

### 1.2 Spec-Driven Development
Every major feature, workflow, API, agent, and state transition must originate from an approved specification before implementation begins. No direct implementation is allowed without a defined spec.

### 1.3 Mobile-First Experience
The primary user experience targets Android mobile devices using Expo React Native. All interfaces, flows, validations, and interactions must be optimized for mobile responsiveness and low-friction usability.

### 1.4 Explainable AI Governance
Every important AI-driven decision must expose:
* reasoning traces
* ranking calculations
* confidence scores
* fallback logic
* workflow transitions
* rejection explanations

All traces must be persisted to the `agentTraces` collection.

### 1.5 Simulation Before Real Dependency
The platform must prefer simulation-safe workflows and mock datasets during development and demonstrations. Synthetic datasets must always contain:
```json
{
  "isSynthetic": true
}
```

## Architecture Principles

### 2.1 Multi-Agent Orchestration Architecture
The system must use structured multi-agent orchestration with isolated responsibilities.

Core orchestration agents include:

1. Intent Parsing Agent
2. Provider Matching Agent
3. Dynamic Pricing Agent
4. Scheduling Agent
5. Booking Agent
6. Follow-Up Automation Agent
7. Dispute Resolution Agent

Each agent must:

* expose explicit interfaces
* operate independently
* avoid hidden coupling
* return structured outputs only

### 2.2 Strict Separation of Responsibilities
The system must enforce separation between:

* frontend UI
* orchestration logic
* AI reasoning
* ranking systems
* backend APIs
* database access

Frontend layers must never contain:

* provider scoring logic
* orchestration pipelines
* ranking formulas
* AI reasoning implementation

### 2.3 API-Centric System Design
All orchestration, workflows, and business operations must be exposed through backend APIs.

Every API response must follow this structure:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

No inconsistent response shapes are allowed.

### 2.4 State Machine Enforcement
All workflows must operate through explicit state transitions.

Mandatory booking lifecycle:

```text
pending → matched → confirmed → in_progress → completed
```

Dispute branch:

```text
disputed → resolved
```

Every transition must:

* include timestamps
* append to `timeline[]`
* include triggering agent metadata
* include reasoning context

### 2.5 Fallback-First Engineering
Every critical workflow must define fallback behavior before implementation.

Mandatory fallback examples:

* No provider match → expand search radius + suggest alternatives
* Provider cancellation → auto-reassign next ranked provider
* Schedule conflict → return alternative slots
* Maps API failure → use local distance estimation fallback
* AI parsing uncertainty → request clarification immediately

No critical workflow may exist without fallback handling.

## Technology Constraints

### 3.1 Frontend Stack
Mandatory frontend technologies:

* React Native
* Expo
* TypeScript
* Expo EAS Build

Rules:

* No implicit `any`
* Strict TypeScript enabled
* Mobile-first UI only

### 3.2 Backend Stack
Mandatory backend stack:

* Python 3.12+
* FastAPI
* Pydantic validation
* Async-first architecture

Rules:

* No untyped public functions
* No blocking synchronous AI calls
* No business logic inside route handlers

### 3.3 AI & Orchestration Stack
Mandatory AI stack:

* Google Gemini API
* Google Antigravity orchestration framework

Rules:

* Agent outputs must be validated before persistence
* Raw LLM outputs must never directly update Firestore
* Prompt execution must remain deterministic where possible

### 3.4 Database & Storage Constraints
Mandatory database:

* Firebase Firestore

Authentication:

* Firebase Authentication

Rules:

* No direct Firestore writes from frontend
* All writes must pass backend validation
* Collections must remain logically segmented

### 3.5 Maps & Geolocation
Primary services:

* Google Places API
* Geocoding API
* Distance Matrix API

Fallback requirement:

* Local approximation logic when APIs fail

## AI Governance & Decision Rules

### 4.1 Explainable Ranking
Every provider recommendation must include:

* final score
* confidence metric
* ranking explanation
* rejection reasons
* pricing justification
* availability reasoning

### 4.2 Immutable Ranking Formula
Provider ranking must always use the standardized weighted formula.

The ranking engine must never rely solely on:

* distance
* price
* ratings

Balanced multi-factor scoring is mandatory.

### 4.3 Multilingual Parsing Rules
The system must support:

* English
* Urdu
* Roman Urdu
* mixed-language prompts

Confidence handling rule:

* Confidence ≥ 0.70 → continue workflow
* Confidence < 0.70 → stop execution and ask exactly one clarification question

### 4.4 Output Validation Requirements
All AI-generated outputs must be validated before database persistence.

Validation must reject:

* invalid schedules
* overlapping bookings
* malformed prices
* unsupported categories
* impossible timestamps
* corrupted workflow states

## Code Quality Standards

### 5.1 Modular Engineering
Every feature begins as an isolated module before integration.

Rules:

* No cross-module internal imports
* Shared utilities only through explicit interfaces
* Business logic must remain reusable and testable

### 5.2 Function Standards
Rules:

* Functions should remain under 50 lines where practical
* Public classes and functions require docstrings
* Strong typing required everywhere
* Avoid `Any` unless technically unavoidable

### 5.3 Testing Requirements
Mandatory testing rules:

* Core orchestration logic must be tested
* Ranking systems require deterministic tests
* Workflow state transitions require integration tests
* Critical utilities require near-complete coverage

Test-first implementation is preferred for orchestration-critical modules.

### 5.4 Logging & Observability
The system must log:

* workflow transitions
* agent execution traces
* fallback activations
* API failures
* validation failures

The system must never log:

* raw secrets
* access tokens
* private user payloads
* sensitive request bodies

## Security & Data Governance

### 6.1 Secret Management
All secrets must use:

* `.env`
* secure environment variables
* protected runtime configuration

Hardcoded credentials are strictly prohibited.

### 6.2 Input Validation
Every API boundary must use strict validation through Pydantic schemas.

No unvalidated payload may:

* trigger workflows
* call agents
* write to Firestore

### 6.3 Auditability
All state-changing operations must generate:

* audit metadata
* timestamps
* actor identity
* triggering agent reference

## Workflow & Collaboration Rules

### 7.1 Clarification Rule
When specifications are ambiguous:

* ask one focused clarification question
* avoid assumptions for critical workflows

### 7.2 Architectural Decision Rule
For major architectural decisions:

* propose multiple implementation approaches
* explain tradeoffs
* wait before irreversible implementation

### 7.3 Commit Convention
follow:

```text
type(scope): description
```

Examples:

```text
feat(matching): add multilingual provider ranking
fix(booking): resolve state transition rollback issue
```

### 7.4 Constitution Enforcement
Any violation against this constitution must be:

* explicitly flagged
* documented
* corrected before continuation

## Mandatory Demo Requirements

The prototype must successfully demonstrate:

1. Multilingual intent parsing
2. AI-driven provider ranking
3. Explainable recommendation traces
4. State-machine workflow transitions
5. Automated follow-up orchestration
6. At least one dispute-resolution execution
7. Real-time agent trace visibility
8. Fallback execution scenarios
9. End-to-end booking simulation

## Governance
This Constitution supersedes all other practices; Amendments require documentation, approval, and a migration plan. All PRs/reviews must verify compliance; Complexity must be justified.

**Version**: 1.0.0 | **Ratified**: 2026-05-17 | **Last Amended**: 2026-05-17
