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
        categories = ["AC Technician", "Plumber", "Electrician", "Beautician", "Appliance Repair", "Tutor"]
        names_prefix = ["Ali", "Khan", "Ahmed", "Karachi", "Express", "Smart", "Quick", "Super", "Zain", "Raza"]
        category_suffixes = {
            "AC Technician": ["HVAC", "AC Experts", "Cooling", "AC Solutions", "AC Repair"],
            "Plumber": ["Plumbing", "Pipes", "Plumbers", "Leak Fixers", "Sanitary"],
            "Electrician": ["Electric", "Wiring", "Sparks", "Electricians", "Power"],
            "Beautician": ["Salon", "Beauty", "Makeup", "Glamour", "Aesthetics"],
            "Appliance Repair": ["Appliance Fix", "Repairs", "Home Tech", "Appliances", "Fixers"],
            "Tutor": ["Math Tutor", "Science Academy", "Tutors", "English Expert", "Academy"]
        }
        locations = list(KARACHI_CENTROIDS.keys())
        tiers = ["gold", "silver", "standard"]
        
        seeded = []
        random.seed(101) # Deterministic data across tests
        
        for i in range(1, 61):
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
            
            cancellation_rate = round(random.uniform(0.0, 0.2), 2)
            reliability_score = round(random.uniform(0.7, 1.0), 2)
            review_recency = random.randint(1, 30)
            capacity_slots = random.randint(1, 5)
            active_jobs_this_week = random.randint(0, 15)
            base_price = round(random.uniform(800.0, 3500.0), 2)
            
            seeded.append({
                "provider_id": f"PRO-{1000 + i}",
                "name": name,
                "category": category,
                "base_location": base_loc,
                "latitude": lat,
                "longitude": lon,
                "rating": rating,
                "tier": tier,
                "cancellation_rate": cancellation_rate,
                "reliability_score": reliability_score,
                "review_recency": review_recency,
                "capacity_slots": capacity_slots,
                "active_jobs_this_week": active_jobs_this_week,
                "base_price": base_price
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

                floored_distance = max(1.2, distance_km)

                # Normalize 7 factors (score between 0.0 and 1.0, where 1.0 is best)
                norm_distance = max(0.0, 1.0 - (floored_distance / 30.0))
                norm_rating = p["rating"] / 5.0
                norm_reliability = p["reliability_score"]
                norm_price = max(0.0, 1.0 - (p["base_price"] / 4000.0))
                norm_cancellation = max(0.0, 1.0 - (p["cancellation_rate"] / 0.5))
                norm_recency = max(0.0, 1.0 - (p["review_recency"] / 30.0))
                norm_workload = max(0.0, 1.0 - (p["active_jobs_this_week"] / 20.0)) # Lower workload gets a boost

                # Apply Weights (Sum = 1.0)
                # Distance: 0.20, Rating: 0.20, Reliability: 0.15, Price: 0.15, Cancellation: 0.10, Recency: 0.10, Workload: 0.10
                match_score = (
                    (norm_distance * 0.20) +
                    (norm_rating * 0.20) +
                    (norm_reliability * 0.15) +
                    (norm_price * 0.15) +
                    (norm_cancellation * 0.10) +
                    (norm_recency * 0.10) +
                    (norm_workload * 0.10)
                )
                match_score = round(max(0.1, min(1.0, match_score)), 3)

                matched_list.append({
                    "provider_id": p["provider_id"],
                    "name": p["name"],
                    "category": p["category"],
                    "distance_km": floored_distance,
                    "rating": p["rating"],
                    "tier": p["tier"],
                    "cancellation_rate": p["cancellation_rate"],
                    "reliability_score": p["reliability_score"],
                    "review_recency": p["review_recency"],
                    "capacity_slots": p["capacity_slots"],
                    "active_jobs_this_week": p["active_jobs_this_week"],
                    "base_price": p["base_price"],
                    "match_score": match_score,
                })

        # Sort descending by match_score (highest score first)
        matched_list.sort(key=lambda x: x["match_score"], reverse=True)

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