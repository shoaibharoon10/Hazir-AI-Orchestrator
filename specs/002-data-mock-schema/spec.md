## Part 1: Reference Architecture Analysis
- Patterns for high-performance NoSQL indexing in Firebase Firestore for geolocation and multi-factor filtering.
- What traditional booking systems do poorly (e.g., rigid relational joins, single-factor distance sorting).
- Strategic design decisions for structuring synthetic datasets with `isSynthetic: true`.

## Part 2: Current Architecture Analysis
- Constraints imposed by Constitution v3.1 regarding Type A (Read-Only Mock Data) and Type B (Runtime Organic Data).
- Fields explicitly required to fulfill the Immutable 8-Factor Ranking Formula (rating, cancellationRate, reliabilityScore, distance vectors, specializationMatch, basePrice, reviewRecency, availability).
- Affected files: backend schemas, seeding scripts, and data models.

## Part 3: Implementation Plan
- Phased approach for seeding data (`runSeed.js`) and validating data formats before backend orchestration starts.
- Risk mitigation for straight-line distance fallback if Google Maps Distance Matrix API fails or is throttled.

## Part 4: Implementation Checklist
- Strict Pydantic and TypeScript type definitions for `providers`, `providerSchedules`, `reviews`, `bookings`, and `agentTraces` collections.
- Setup script definitions with hardcoded synthetic provider examples for AC technicians, electricians, and plumbers.

## Constraints
- Explicit boundaries: Frontend must NEVER write directly to Type A mock collections. 
- Schema parameters must reject zero or negative values for validation safety.

## Success Criteria
- Fully validated JSON format matching the 8-factor mathematical model requirements with zero implicit types.
- Acceptance tests simulating data fetching for Acceptance Test 1 (AC Technician scenario).