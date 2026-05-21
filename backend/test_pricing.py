import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.schemas.pricing import PricingRequestInput
from src.services.pricing_service import PricingService

def run_tests():
    ps = PricingService()
    
    req1 = PricingRequestInput(
        job_category="AC Technician",
        complexity_tier="complex",
        distance_km=10.0,
        urgency_flag=True,
        loyalty_tier=None,
        provider_base_rate=1200.0  # Provider A
    )
    
    req2 = PricingRequestInput(
        job_category="AC Technician",
        complexity_tier="complex",
        distance_km=10.0,
        urgency_flag=True,
        loyalty_tier=None,
        provider_base_rate=2500.0  # Provider B
    )
    
    res1 = ps.calculate_net_total(req1)
    res2 = ps.calculate_net_total(req2)
    
    print("Provider A (1200 Base) -> Breakdown:", res1.dict())
    print("Provider B (2500 Base) -> Breakdown:", res2.dict())

if __name__ == "__main__":
    run_tests()
