from typing import Optional
from src.schemas.pricing import PricingRequestInput, PriceBreakdownOutput

class PricingService:
    """
    Deterministic pricing engine implementing a 5-factor mathematical financial calculator.
    """
    BASE_RATES = {
        "basic": 1000.00,
        "intermediate": 1800.00,
        "complex": 3000.00
    }
    
    SURGE_MULTIPLIER = 0.20 # 20% surge for urgency
    MAX_SURGE_CAP = 0.50 # Hard-cap surge at 50% of base price
    
    DISTANCE_BASELINE_KM = 5.0
    DISTANCE_CHARGE_PER_KM = 25.00
    
    LOYALTY_DISCOUNTS = {
        "silver": 50.00,
        "gold": 150.00
    }

    def evaluate_base_price(self, tier: str) -> float:
        """T004: Rule-based complexity evaluation matrix."""
        return self.BASE_RATES.get(tier.lower(), 1000.00)

    def calculate_surge(self, base_price: float, urgency_flag: bool) -> float:
        """T005: Dynamic surge multiplier calculation with hard-cap overflow ceiling."""
        if not urgency_flag:
            return 0.00
            
        calculated_surge = base_price * self.SURGE_MULTIPLIER
        max_surge = base_price * self.MAX_SURGE_CAP
        
        return min(calculated_surge, max_surge)

    def calculate_distance_buffer(self, distance_km: float) -> float:
        """T006: Geospatial distance buffer cost calculation handling 0km boundary natively."""
        if distance_km <= self.DISTANCE_BASELINE_KM:
            return 0.00
            
        billable_km = distance_km - self.DISTANCE_BASELINE_KM
        return max(0.00, billable_km * self.DISTANCE_CHARGE_PER_KM)

    def calculate_discount(self, loyalty_tier: Optional[str]) -> float:
        """T007: Historical loyalty tier discount logic."""
        if not loyalty_tier:
            return 0.00
            
        return self.LOYALTY_DISCOUNTS.get(loyalty_tier.lower(), 0.00)

    def calculate_net_total(self, request: PricingRequestInput) -> PriceBreakdownOutput:
        """T008: Composite logic enforcing 2-decimal rounding strictness."""
        base_price = self.evaluate_base_price(request.complexity_tier)
        surge_cost = self.calculate_surge(base_price, request.urgency_flag)
        distance_buffer = self.calculate_distance_buffer(request.distance_km)
        discount = self.calculate_discount(request.loyalty_tier)
        
        raw_net = (base_price + surge_cost + distance_buffer) - discount
        # Ensure net_total doesn't drop below 0 if discounts are overly generous
        net_total = max(0.00, raw_net)
        
        return PriceBreakdownOutput(
            base_price=round(base_price, 2),
            surge_cost=round(surge_cost, 2),
            distance_buffer=round(distance_buffer, 2),
            discount=round(discount, 2),
            net_total=round(net_total, 2)
        )
