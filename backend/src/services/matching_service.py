import math
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in kilometers between two points on the earth."""
    R = 6371.0 # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

# Mock Geocoder for Karachi areas
LOCATION_COORDS = {
    "clifton block 9": (24.8166, 67.0236),
    "dha phase 6": (24.8016, 67.0425),
    "gulshan": (24.9180, 67.0971),
    "johar": (24.9142, 67.1256),
    "default": (24.8607, 67.0011) # Central Karachi
}

class ProviderMatchingEngine:
    """
    Deterministic matching engine executing the 6-factor algorithm to rank providers.
    """
    def __init__(self) -> None:
        self.MAX_DISTANCE_KM = 30.0
        self.WEIGHT_DISTANCE = 0.30
        self.WEIGHT_RATING = 0.25
        self.WEIGHT_RELIABILITY = 0.25
        self.WEIGHT_SKILLS = 0.10
        self.WEIGHT_RECENCY = 0.10

    def resolve_location(self, location_context: Optional[str]) -> tuple[float, float]:
        if not location_context:
            return LOCATION_COORDS["default"]
        
        loc_lower = location_context.lower()
        for key, coords in LOCATION_COORDS.items():
            if key in loc_lower:
                return coords
        return LOCATION_COORDS["default"]

    def calculate_distance_score(self, distance_km: float) -> float:
        if distance_km > self.MAX_DISTANCE_KM:
            return 0.0
        # Closer is better. 0 km = 1.0, MAX_DISTANCE = 0.0
        return max(0.0, 1.0 - (distance_km / self.MAX_DISTANCE_KM))

    def evaluate_availability(self, time_preference: Optional[str], provider_schedules: List[Dict]) -> bool:
        """
        Matrix availability check.
        For MVP, if provider has any schedule block, we assume overlapping availability.
        """
        if not time_preference:
            return True
        return len(provider_schedules) > 0

    def calculate_rating_score(self, rating: float) -> float:
        # Rating is out of 5.0
        return max(0.0, min(1.0, rating / 5.0))

    def calculate_reliability_score(self, reliability: float, cancellation: float) -> float:
        # High reliability is good, high cancellation is penalizing.
        base = reliability - (cancellation * 0.5)
        return max(0.0, min(1.0, base))

    def calculate_recency_score(self, review_recency_days: float) -> float:
        # Closer to 0 days is better. > 30 days = 0 score.
        if review_recency_days > 30:
            return 0.0
        return max(0.0, 1.0 - (review_recency_days / 30.0))

    def calculate_skill_score(self, query_context: str, specializations: List[str]) -> float:
        # Map specific technical tags
        if not query_context:
            return 0.5 
            
        q_lower = query_context.lower()
        matches = [s for s in specializations if s.lower() in q_lower or q_lower in s.lower()]
        
        if matches:
            return 1.0
        return 0.0

    def match_and_rank(self, request: Any, providers: List[Dict], schedules: List[Dict]) -> List[Dict]:
        """
        Applies the 6-factor algorithm to score and rank candidate providers.
        Returns array of ranked providers sorted by composite_score.
        """
        user_lat, user_lon = self.resolve_location(request.location_context)
        ranked_providers = []

        for provider in providers:
            # 1. Geospatial Distance (Haversine)
            prov_lat = provider.get('distanceVectors', {}).get('lat', user_lat)
            prov_lon = provider.get('distanceVectors', {}).get('lng', user_lon)
            dist_km = haversine_distance(user_lat, user_lon, prov_lat, prov_lon)
            
            # 2. Matching Availability Matrix
            prov_schedules = [s for s in schedules if s.get('providerId') == provider.get('id')]
            is_available = self.evaluate_availability(request.time_preference, prov_schedules)
            
            if not is_available:
                continue # Strictly exclude unavailable providers
                
            dist_score = self.calculate_distance_score(dist_km)
            
            # 3. Global Rating Weights
            rating_score = self.calculate_rating_score(provider.get('rating', 0.0))
            
            # 4. Review Recency Scoring
            recency_score = self.calculate_recency_score(provider.get('reviewRecency', 30.0))
            
            # 5. Historical Reliability Data
            reliability_score = self.calculate_reliability_score(
                provider.get('reliabilityScore', 0.0),
                provider.get('cancellationRate', 0.0)
            )
            
            # 6. Technical Skill Specialization
            skill_score = self.calculate_skill_score(request.service_category, provider.get('specializations', []))

            # Composite Normalized Score
            composite_score = (
                (dist_score * self.WEIGHT_DISTANCE) +
                (rating_score * self.WEIGHT_RATING) +
                (reliability_score * self.WEIGHT_RELIABILITY) +
                (skill_score * self.WEIGHT_SKILLS) +
                (recency_score * self.WEIGHT_RECENCY)
            )
            
            # Urgency penalty: If urgent, penalize providers that are far
            if request.urgency_level in ["urgent", "very urgent"] and dist_km > 10.0:
                composite_score *= 0.8

            ranked_providers.append({
                "id": provider.get('id'),
                "name": provider.get('name'),
                "category": provider.get('category'),
                "composite_score": round(composite_score, 3),
                "distance_km": round(dist_km, 2),
                "matched_skills": provider.get('specializations', []),
                "is_available": is_available
            })

        # Sort descending by composite score
        ranked_providers.sort(key=lambda x: x['composite_score'], reverse=True)
        return ranked_providers
