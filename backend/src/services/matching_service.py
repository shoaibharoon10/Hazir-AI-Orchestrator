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

    def match_providers(self, category: str, location_text: str) -> dict:
        normalized_loc = location_text.lower().strip()

        # Resolve user centroid — default to sadar if no known token found
        user_lat, user_lon = KARACHI_CENTROIDS["sadar"]
        for loc_key, coords in KARACHI_CENTROIDS.items():
            if loc_key in normalized_loc:
                user_lat, user_lon = coords
                break

        matched_list = []

        for p in self.providers:
            if p["category"] == category:  # Strict exact string equality
                lat_diff = p["latitude"] - user_lat
                lon_diff = p["longitude"] - user_lon
                distance_km = round(math.sqrt(lat_diff**2 + lon_diff**2) * 111.0, 2)

                match_score = round((5.0 - (distance_km / 10.0)) * 0.6 + (p["rating"] * 0.4), 2)
                match_score = max(0.1, min(1.0, match_score))
                floored_distance = max(1.2, distance_km)

                matched_list.append({
                    "provider_id": p["provider_id"],
                    "name": p["name"],
                    "category": p["category"],
                    "distance_km": floored_distance,
                    "rating": p["rating"],
                    "tier": p["tier"],
                    "match_score": match_score,
                })

        # Sort ascending by distance (closest first)
        matched_list.sort(key=lambda x: x["distance_km"])

        if not matched_list:
            logger.warning(f"No providers found for category '{category}' near '{location_text}'")
            return {"best_match": None, "alternatives": []}

        # Build selection_reasoning for the winner only
        winner = matched_list[0]
        winner["selection_reasoning"] = (
            f"Selected '{winner['name']}' because they are the closest available "
            f"{winner['tier'].capitalize()}-Tier provider within {winner['distance_km']}km "
            f"of {location_text} with a {winner['rating']}/5.0 rating."
        )

        alternatives = matched_list[1:3]  # Top 2 alternatives

        logger.info(
            f"[MatchingAgent] {len(matched_list)} candidates for '{category}' near '{location_text}'. "
            f"Best: {winner['name']} @ {winner['distance_km']}km. Alternatives: {len(alternatives)}."
        )
        return {"best_match": winner, "alternatives": alternatives}