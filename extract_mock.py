import os
import sys

# Add backend directory to sys.path so we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from src.services.matching_service import ProviderMatchingEngine
from src.services.pricing_service import PricingService

def main():
    engine = ProviderMatchingEngine()
    pricing = PricingService()
    
    providers = engine.providers
    total = len(providers)
    
    print(f"==================================================")
    print(f"MOCK DATA EXTRACTION SUMMARY")
    print(f"==================================================")
    print(f"Total Mock Providers Found: {total}")
    print(f"--------------------------------------------------")
    
    print(f"{'ID':<10} | {'NAME':<25} | {'CATEGORY':<18} | {'BASE FEE':<10} | {'LOCATION'}")
    print("-" * 80)
    
    for p in providers:
        tier = p.get('tier', 'standard')
        # Since matching_service uses gold/silver/standard and pricing_service expects basic/intermediate/complex,
        # we will map them or just use the pricing service if it has a default.
        # Actually, let's just print the tier if we don't know the exact fee mapping, or we can see what pricing service does.
        # pricing service defaults to 1000.0 if not found.
        # Let's map gold -> complex (3000), silver -> intermediate (1800), standard -> basic (1000)
        mapped_tier = "basic"
        if tier == "gold":
            mapped_tier = "complex"
        elif tier == "silver":
            mapped_tier = "intermediate"
            
        base_fee = pricing.evaluate_base_price(mapped_tier)
        
        name = p.get('name', 'Unknown')
        category = p.get('category', 'Unknown')
        location = p.get('base_location', 'Unknown')
        pid = p.get('provider_id', 'Unknown')
        
        print(f"{pid:<10} | {name:<25} | {category:<18} | PKR {base_fee:<6} | {location.capitalize()}")

if __name__ == '__main__':
    main()
