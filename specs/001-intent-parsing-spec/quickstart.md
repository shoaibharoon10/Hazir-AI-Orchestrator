# Quickstart Guide: Intent Parsing Agent

This guide provides a quick overview of how to interact with the Intent Parsing Agent.

## Endpoint

-   **POST** `/api/orchestrate/intent`

## Request Body

```json
{
  "user_request": "string"
}
```

**`user_request`**: The natural language input from the user, which can be in English, Urdu, Roman Urdu, or mixed languages.

## Success Response (Confidence >= 0.70)

```json
{
  "success": true,
  "data": {
    "service_category": "AC Technician",
    "location_context": "Clifton block 9",
    "time_preference": "today 5 PM",
    "urgency_level": "very urgent",
    "confidence_score": 0.95
  },
  "error": null
}
```

## Low Confidence Response (Confidence < 0.70)

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "LOW_CONFIDENCE",
    "message": "Are you looking for an electrician or something else?",
    "confidence_score": 0.65
  }
}
```

## Error Response (Invalid Input or Internal Error)

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "The provided user request is malformed or empty."
  }
}
```

## Example Usage (Python with `requests`)

```python
import requests
import json

API_BASE_URL = "http://localhost:8000" # Replace with actual API base URL

def parse_intent(user_request):
    url = f"{API_BASE_URL}/api/orchestrate/intent"
    headers = {"Content-Type": "application/json"}
    payload = {"user_request": user_request}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return {"success": False, "data": None, "error": {"code": "NETWORK_ERROR", "message": str(e)}}

# Example 1: High confidence request
request_1 = "mujhe ac theek karwana hai Clifton block 9 me aj sham 5 baje tak, bohot zaruri hai"
print("\n--- Request 1 ---")
print(f"User Request: {request_1}")
response_1 = parse_intent(request_1)
print(f"API Response: {json.dumps(response_1, indent=2)}")

# Example 2: Ambiguous request triggering low confidence
request_2 = "I need help with my lights"
print("\n--- Request 2 ---")
print(f"User Request: {request_2}")
response_2 = parse_intent(request_2)
print(f"API Response: {json.dumps(response_2, indent=2)}")

# Example 3: Empty request (will result in 400 Bad Request if validation is strict)
request_3 = ""
print("\n--- Request 3 ---")
print(f"User Request: {request_3}")
response_3 = parse_intent(request_3)
print(f"API Response: {json.dumps(response_3, indent=2)}")
```