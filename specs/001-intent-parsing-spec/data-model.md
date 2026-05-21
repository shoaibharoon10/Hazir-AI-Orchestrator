# Data Model: Intent Parsing Agent

## IntentOutput

Represents the structured output of the intent parsing process.

### Fields:

*   **`service_category`**: string (enum: "AC Technician", "Electrician", "Plumber")
    *   **Description**: The category of service requested by the user.
*   **`location_context`**: string
    *   **Description**: The geographical location or area mentioned in the user's request.
*   **`time_preference`**: string
    *   **Description**: The preferred time or timeframe for the service (e.g., "today 5 PM", "tomorrow morning").
*   **`urgency_level`**: string (enum: "normal", "urgent", "very urgent")
    *   **Description**: The perceived urgency of the user's request.
*   **`confidence_score`**: float (range: 0.0 to 1.0)
    *   **Description**: A numerical score indicating the agent's confidence in the extracted intent, where >= 0.70 is considered high confidence.
