# Antigravity Trace: 02. Provider Ranking

**Workplan:**
The Provider Matching Agent receives structured intent (`AC Technician` in `Sadar`). It must filter the synthetic dataset of 60 providers, apply a 7-factor mathematical ranking algorithm to all local matches, and sort the list deterministically.

## Agent Observations
- **Target Category:** AC Technician
- **Target Location:** Sadar Centroid (24.86, 67.01)
- **Local Candidates:** 10 candidates found in memory.

## Reasoning
The agent calculates Euclidean distance vectors for all 10 candidates. Instead of simply picking the closest provider, the engine normalizes 7 distinct factors (Distance, Rating, Reliability, Base Price, Cancellation Rate, Review Recency, and Workload Balancing) against a 0.0 to 1.0 scale, multiplying them by their assigned weights.

## Decisions
- Discard non-Sadar candidates for this evaluation.
- Boost providers with fewer `active_jobs_this_week` (Workload Equity).
- Select the provider with the highest sum total `match_score`.

## Tool Calls
- `ProviderMatchingEngine.match_providers("AC Technician", "sadar")`

## Action Execution
**Algorithm Normalization (Example Top Pick):**
- Name: Khan AC Experts #120
- Distance: 2.1km (Score: 0.93 * 0.20 weight)
- Rating: 4.8/5.0 (Score: 0.96 * 0.20 weight)
- Reliability: 0.95 (Score: 0.95 * 0.15 weight)
- Workload: 2 active jobs (Score: 0.90 * 0.10 weight)
- **Final Normalized Match Score:** 0.892

## Error Recovery
None required. 10 candidates were successfully evaluated.

## Final Outcomes
"Khan AC Experts #120" is selected as the `best_match` due to an optimal balance of proximity, high rating, and low current workload. The top 2 alternatives are securely packaged into the orchestration output payload.
