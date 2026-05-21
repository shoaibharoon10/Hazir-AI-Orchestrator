import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.schemas.unified import UnifiedOrchestratorInput
from src.services.unified_service import UnifiedOrchestratorService

def print_trace(title, trace):
    print(f"\n{'='*50}\n{title}\n{'='*50}")
    for idx, t in enumerate(trace):
        print(f"[{idx+1}] {t['agent']} - {t['action']}")
        print(f"    Thought: {t['thought']}")

def run_tests():
    us = UnifiedOrchestratorService()

    # Test 1: Successful trace
    req1 = UnifiedOrchestratorInput(query="i need an electrician in clifton urgently at 3 pm", customer_id="CUST-10", user_location="unknown")
    res1 = us.run_pipeline(req1)
    print_trace("SUCCESSFUL TRACE", res1.agent_trace)

    # Test 2: Duplicate booking trace
    res2 = us.run_pipeline(req1) # Exact same request
    print_trace("DUPLICATE BOOKING TRACE", res2.agent_trace)

    # Test 3: Fallback trace (gibberish query)
    req3 = UnifiedOrchestratorInput(query="ac in clifton at 4 pm", customer_id="CUST-10", user_location="unknown")
    res3 = us.run_pipeline(req3)
    print_trace("FALLBACK TRACE", res3.agent_trace)

if __name__ == "__main__":
    run_tests()
