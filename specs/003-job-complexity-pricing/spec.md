# Feature Specification: Job Complexity & Dynamic Pricing Engine

**Feature Branch**: `003-job-complexity-pricing`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "Milestone 3: Job Complexity & Dynamic Pricing Engine"

---

## Part 1: Reference Architecture Analysis

- **Complexity Evaluation**: Rule-based complexity evaluation matrices based on parsed service intent keywords (e.g., "leak", "wiring", "installation") and urgency flags (e.g., "urgent", "normal").
- **Dynamic Pricing Computation**: Design patterns incorporating multi-variable surge factors (e.g., late-night scheduling, extreme urgency), geospatial distance buffers (added travel costs for distant providers), and historical loyalty tier discounts for returning users.

## Part 2: Current Architecture Analysis

- **Integration Pipelines**: Takes the active outputs of both `/api/orchestrate/intent` (providing urgency and time contexts) and `/api/orchestrate/match` (providing the matched provider's distance and default base price).
- **Business Rules (Categorization)**: Maps jobs into three strict categories:
  - **Basic**: Standard flat rate structure.
  - **Intermediate**: Hourly scale structure.
  - **Complex**: Requires custom base price variables + technician specialization multiplier.
- **Affected Files**:
  - `backend/src/services/pricing_service.py` (new algorithm engine)
  - `backend/src/api/orchestrate/pricing.py` (new FastAPI router)
  - Existing payload validation schemas in `backend/src/schemas/`.

## Part 3: Implementation Plan

1. **Code Scaffolding**: Define the Pydantic input and output structures for the pricing engine.
2. **Mathematical Calculation Logic**: Build isolated deterministic functions for the distance buffer, urgency surge, complexity categorization, and loyalty discounts inside `pricing_service.py`.
3. **Router Wiring**: Build the FastAPI router endpoint at `/api/orchestrate/price` that maps the request into the pricing service and wraps the response.
4. **Edge-case Handling**: Ensure robust safety checks preventing overflow surge calculations (e.g., a cap limit on surges) and graceful zero-distance or division-by-zero validation fallbacks wrapped seamlessly in our `APIResponseSchema`.

## Part 4: Implementation Checklist

- Define `PricingRequestInput` schema mapping intent outputs and provider match data.
- Define `PriceBreakdownOutput` schema explicitly detailing `base_price`, `surge_cost`, `distance_buffer`, `discount`, and `net_total`.
- Prepare Pytest scenarios evaluating precise rounding logic (strictly 2 decimal places) and mathematical compliance metrics for deterministic testing.

## Constraints

- **Determinism**: All calculated financial objects MUST use standard float/decimal formats.
- **Isolation**: Pricing computations must remain entirely deterministic and strictly detached from generative LLM prompt layers (LLMs interpret text, the backend calculates the money).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Flat-Rate Computation (Priority: P1)

A user is matched with a local plumber for a basic "sink leak" during normal working hours.

**Why this priority**: Validates the baseline functionality of the dynamic pricing engine without surge or multiplier overrides.

**Independent Test**: Can be tested by sending a mocked payload with a "normal" urgency intent and a short-distance provider (e.g., 2km away).

**Acceptance Scenarios**:
1. **Given** a normal urgency request for a basic repair, **When** the pricing engine computes the cost, **Then** it returns the provider's base flat rate + a standard minimal distance buffer, with exactly zero surge applied.

### User Story 2 - Complex Job with Urgent Surge (Priority: P2)

A user requires an "AC Installation" (Complex) at 2:00 AM (Urgent/Late Night) from a provider 25km away.

**Why this priority**: Validates the upper boundary and mathematical combination of all modifiers (complexity multiplier + surge + heavy distance buffer).

**Independent Test**: Send an urgent, late-night, long-distance payload to the engine.

**Acceptance Scenarios**:
1. **Given** an urgent, complex, distant job, **When** computed, **Then** the `PriceBreakdownOutput` explicitly breaks out the surge cost, distance buffer, and specialization multiplier accurately, summing to the exact expected net total.

---

## Edge Cases

- **Zero-Distance Check**: What happens if the calculated distance is 0km? (The distance buffer natively calculates to 0.0 without throwing division errors).
- **Surge Overflow**: What happens if multiple surge triggers stack (e.g., holiday + urgent + late-night)? (Apply a hard-cap ceiling to the surge factor, e.g., max 2.0x base price).
- **Missing Data**: What if the provider's base price is null? (Engine must catch this exception and return an error gracefully via `APIResponseSchema` without crashing).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST categorize jobs into Basic, Intermediate, or Complex based on keyword heuristics.
- **FR-002**: System MUST apply a geospatial distance buffer cost proportional to provider proximity.
- **FR-003**: System MUST calculate an urgency/time-based surge factor.
- **FR-004**: System MUST standardize and return all financial values formatted accurately as rounded floats (2 decimal places).
- **FR-005**: All output MUST be wrapped in the universal `APIResponseSchema`.

### Key Entities

- **PricingRequestInput**: Merged data context representing the parsed user intent and the matched provider's base price and distance.
- **PriceBreakdownOutput**: Financial structure holding `base_price`, `surge_cost`, `distance_buffer`, `discount`, and `net_total`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The pricing engine computes the final JSON financial breakdown deterministically in under 100ms.
- **SC-002**: The mathematical rounding logic consistently prevents floating-point precision anomalies (e.g., returning 1500.00 instead of 1499.9999).
- **SC-003**: 100% of generated responses strictly adhere to the `APIResponseSchema` contract.
