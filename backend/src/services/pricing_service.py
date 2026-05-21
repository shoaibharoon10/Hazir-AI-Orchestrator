from typing import Optional
import logging
from src.schemas.pricing import PricingRequestInput, PriceBreakdownOutput

logger = logging.getLogger(__name__)

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
        
        if calculated_surge > max_surge:
            logger.warning(f"Calculated surge ({calculated_surge}) exceeded maximum surge cap ({max_surge}). Clamping to max allowed surge.")
            
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
        complexity_base_rate = self.evaluate_base_price(request.complexity_tier)
        provider_base_rate = request.provider_base_rate
        
        combined_base = complexity_base_rate + provider_base_rate
        
        urgency_surge = self.calculate_surge(combined_base, request.urgency_flag)
        distance_charge = self.calculate_distance_buffer(request.distance_km)
        loyalty_discount = self.calculate_discount(request.loyalty_tier)
        
        raw_net = (combined_base + urgency_surge + distance_charge) - loyalty_discount
        # Ensure net_total doesn't drop below 0 if discounts are overly generous
        final_total = max(0.00, raw_net)
        
        return PriceBreakdownOutput(
            complexity_base_rate=round(complexity_base_rate, 2),
            provider_base_rate=round(provider_base_rate, 2),
            urgency_surge=round(urgency_surge, 2),
            distance_charge=round(distance_charge, 2),
            loyalty_discount=round(loyalty_discount, 2),
            final_total=round(final_total, 2)
        )
