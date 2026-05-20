# Antigravity Trace: 06. Dispute Workflow & Fallback Recovery

**Workplan:**
This trace covers two distinct Edge Cases: a vague initial query triggering the Gatekeeper, and a post-booking provider "No-Show" triggering the Dispute Escalation Agent.

## Scenario A: The AI Gatekeeper Fallback

### Agent Observations
- **User Query:** "mujhe foran banda bhejo" (Send someone immediately)
- **Extracted Intent:** `service_category` = null, `location_context` = null, `urgency` = urgent.

### Reasoning
Gemini could not identify the service category or location. The Intent Agent's Pydantic schema validator detects missing required slots. The system must NOT proceed to matching.

### Decisions
- Halt Pipeline.
- Trigger `SlotFillingError`.

### Action Execution
```json
{
  "success": false,
  "error": "Aap ne service select ki hai, lekin location aur time dono nahi bataye. Kindly apna Karachi area (e.g., Clifton, Johar, DHA) aur preferred time bataein."
}
```

### Error Recovery
The UI elegantly displays the Amber Warning Card, prompting the user to naturally supply the missing information without crashing the app.

---

## Scenario B: The No-Show Dispute

### Agent Observations
- **Booking ID:** BKG-88X92
- **Dispute Reason:** "no-show"
- **Comment:** "Banda aya hi nahi, mera time waste hua."

### Reasoning
The Dispute Agent evaluates the `no-show` literal category. According to our business logic, provider no-shows are high-friction events that require immediate financial resolution.

### Decisions
- Accept payload via `/api/orchestrate/dispute`.
- Automatically trigger "refund initiated" status.

### Tool Calls
- `workflows.py -> submit_dispute()`

### Action Execution
**API Resolution:**
```json
{
  "success": true,
  "data": {
    "booking_id": "BKG-88X92",
    "status": "disputed",
    "resolution_state": "refund initiated"
  },
  "exec_time_ms": 2.10
}
```

### Final Outcomes
The user is instantly placated by the automated refund. The simulated worker logs the event to eventually penalize the provider's `reliability_score` in the Ranking Engine.
