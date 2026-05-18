import math
import logging
import random
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Karachi Centroids Vector Map (Latitude, Longitude)
KARACHI_CENTROIDS = {
    "clifton": (24.82, 67.03),
    "sadar": (24.86, 67.01),
    "gulshan": (24.92, 67.09),
    "johar": (24.91, 67.12),
    "nazimabad": (24.93, 67.03),
    "dha": (24.79, 67.06)
}

class ProviderMatchingEngine:
    def __init__(self):
        # 50 dynamic, realistic providers dataset generation
        self.providers = self._seed_50_providers()

    def _seed_50_providers(self) -> List[Dict[str, Any]]:
        categories = ["AC Technician", "Plumber", "Electrician", "Beautician", "Appliance Repair"]
        names_prefix = ["Ali", "Khan", "Ahmed", "Karachi", "Express", "Smart", "Quick", "Super", "Zain", "Raza"]
        category_suffixes = {
            "AC Technician": ["HVAC", "AC Experts", "Cooling", "AC Solutions", "AC Repair"],
            "Plumber": ["Plumbing", "Pipes", "Plumbers", "Leak Fixers", "Sanitary"],
            "Electrician": ["Electric", "Wiring", "Sparks", "Electricians", "Power"],
            "Beautician": ["Salon", "Beauty", "Makeup", "Glamour", "Aesthetics"],
            "Appliance Repair": ["Appliance Fix", "Repairs", "Home Tech", "Appliances", "Fixers"]
        }
        locations = list(KARACHI_CENTROIDS.keys())
        tiers = ["gold", "silver", "standard"]
        
        seeded = []
        random.seed(101) # Deterministic data across tests
        
        for i in range(1, 51):
            category = categories[i % len(categories)]
            base_loc = locations[i % len(locations)]
            centroid_lat, centroid_lon = KARACHI_CENTROIDS[base_loc]
            
            # Adding slight coordinate variance so providers aren't exactly on top of each other
            lat = centroid_lat + random.uniform(-0.015, 0.015)
            lon = centroid_lon + random.uniform(-0.015, 0.015)
            
            suffix = random.choice(category_suffixes[category])
            name = f"{random.choice(names_prefix)} {suffix} #{100 + i}"
            rating = round(random.uniform(3.8, 5.0), 1)
            tier = random.choice(tiers)
            
            seeded.append({
                "provider_id": f"PRO-{1000 + i}",
                "name": name,
                "category": category,
                "base_location": base_loc,
                "latitude": lat,
                "longitude": lon,
                "rating": rating,
                "tier": tier
            })
        return seeded

    def match_providers(self, category: str, location_text: str) -> List[Dict[str, Any]]:
        normalized_loc = location_text.lower().strip()
        
        # Default user centroid if location text token is not matched directly
        user_lat, user_lon = KARACHI_CENTROIDS.get("sadar") 
        for loc_key, coords in KARACHI_CENTROIDS.items():
            if loc_key in normalized_loc:
                user_lat, user_lon = coords
                break

        matched_list = []
        
        # Filtering and calculating mathematical distance vector
        for p in self.providers:
            if p["category"] == category:  # Strict exact string equality — no fuzzy matching
                # Mathematical Straight-Line Vector Distance to Kilometer conversion (approx 111km per degree)
                lat_diff = p["latitude"] - user_lat
                lon_diff = p["longitude"] - user_lon
                distance_km = round(math.sqrt(lat_diff**2 + lon_diff**2) * 111.0, 2)
                
                # Dynamic matching score based on distance and provider rating
                # Less distance + higher rating = higher score
                match_score = round((5.0 - (distance_km / 10.0)) * 0.6 + (p["rating"] * 0.4), 2)
                match_score = max(0.1, min(1.0, match_score)) # Clamp between 0.1 and 1.0
                
                matched_list.append({
                    "provider_id": p["provider_id"],
                    "name": p["name"],
                    "category": p["category"],
                    "distance_km": max(1.2, distance_km), # Minimum floor boundary
                    "rating": p["rating"],
                    "tier": p["tier"],
                    "match_score": match_score,
                    "selection_reasoning": f"Selected '{p['name']}' because they are the closest available {p['tier'].capitalize()}-Tier provider within {distance_km}km with a {p['rating']} rating."
                })
        
        # Sort dynamically by true Euclidean distance ascending (closest to farthest)
        matched_list.sort(key=lambda x: x["distance_km"])
        
        logger.info(f"Geospatial Matching: Found {len(matched_list)} candidates for {category} near {location_text}")
        return matched_list