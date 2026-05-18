import asyncio
import json
from src.schemas.unified import UnifiedOrchestratorInput
from src.services.unified_service import UnifiedOrchestratorService
from src.api.orchestrate.unified import execute_master_workflow

async def run_tests():
    print("Testing Missing Location...")
    req_missing = UnifiedOrchestratorInput(
        query="Mujhe AC theek karwana hai",
        customer_id="cust_1",
        user_location=""
    )
    res_missing = await execute_master_workflow(req_missing)
    if hasattr(res_missing, "body"):
        print(res_missing.body.decode('utf-8'))
    else:
        print(res_missing.model_dump_json(indent=2))

    print("\nTesting Clifton Location...")
    req_clifton = UnifiedOrchestratorInput(
        query="Mujhe plumber chahye urgently",
        customer_id="cust_2",
        user_location="Clifton"
    )
    res_clifton = await execute_master_workflow(req_clifton)
    if hasattr(res_clifton, "body"):
        print(res_clifton.body.decode('utf-8'))
    else:
        print(res_clifton.model_dump_json(indent=2))

    print("\nTesting Johar Location...")
    req_johar = UnifiedOrchestratorInput(
        query="Electrician ki zaroorat hai",
        customer_id="cust_3",
        user_location="Johar"
    )
    res_johar = await execute_master_workflow(req_johar)
    if hasattr(res_johar, "body"):
        print(res_johar.body.decode('utf-8'))
    else:
        print(res_johar.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(run_tests())
