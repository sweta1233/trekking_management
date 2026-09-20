import random
import math
from typing import List, Dict, Any


def generate_trek_demand_dataset(num_samples: int = 1500) -> List[Dict[str, Any]]:
    """
    Generates realistic historical booking demand dataset with physical correlations.
    Pure-python implementation with zero external DLL dependencies.
    """
    random.seed(42)

    durations = [3, 4, 5, 6, 7, 8, 10, 12]
    difficulties = ["Easy", "Easy to Moderate", "Moderate", "Difficult", "Expert"]
    seasons = ["Spring", "Summer", "Monsoon", "Autumn", "Winter"]

    rows = []

    for _ in range(num_samples):
        duration = random.choice(durations)
        difficulty = random.choice(difficulties)
        season = random.choice(seasons)

        if difficulty == "Easy":
            max_altitude = random.randint(2200, 3200)
            base_price = 6000 + duration * 700
        elif difficulty in ["Easy to Moderate", "Moderate"]:
            max_altitude = random.randint(3200, 4300)
            base_price = 8000 + duration * 900
        elif difficulty == "Difficult":
            max_altitude = random.randint(4300, 5200)
            base_price = 11000 + duration * 1100
        else:
            max_altitude = random.randint(5000, 6100)
            base_price = 16000 + duration * 1500

        price = base_price + random.randint(-1500, 2500)
        rating_avg = round(random.uniform(3.8, 5.0), 2)
        is_weekend_start = 1 if random.random() > 0.45 else 0
        discount_pct = random.choice([0.0, 0.05, 0.10, 0.15, 0.20])
        total_slots = random.choice([15, 20, 25, 30])

        # Feature Encodings
        s_spring = 1 if season == "Spring" else 0
        s_summer = 1 if season == "Summer" else 0
        s_monsoon = 1 if season == "Monsoon" else 0
        s_autumn = 1 if season == "Autumn" else 0
        s_winter = 1 if season == "Winter" else 0

        d_easy = 1 if difficulty == "Easy" else 0
        d_moderate = 1 if "Moderate" in difficulty else 0
        d_difficult = 1 if difficulty == "Difficult" else 0
        d_expert = 1 if difficulty == "Expert" else 0

        # Ground Truth Demand Generation Formula + Gaussian Noise
        base_demand = 12.0
        season_weight = 1.35 if s_autumn else (1.25 if s_summer else (0.65 if s_monsoon else 1.0))
        diff_weight = 1.2 if (d_easy or d_moderate) else 0.8
        price_weight = 1.0 - (price - 9000) / 45000
        rating_weight = (rating_avg / 4.5) ** 1.8
        weekend_boost = 2.5 if is_weekend_start else 0.0
        discount_boost = discount_pct * 10.0
        noise = random.gauss(0, 1.2)

        target_demand = (
            base_demand * season_weight * diff_weight * price_weight * rating_weight
            + weekend_boost + discount_boost + noise
        )
        target_demand = max(2, min(total_slots, int(round(target_demand))))

        rows.append({
            "duration_days": duration,
            "max_altitude_m": max_altitude,
            "price": float(price),
            "rating_avg": rating_avg,
            "season_spring": s_spring,
            "season_summer": s_summer,
            "season_monsoon": s_monsoon,
            "season_autumn": s_autumn,
            "season_winter": s_winter,
            "diff_easy": d_easy,
            "diff_moderate": d_moderate,
            "diff_difficult": d_difficult,
            "diff_expert": d_expert,
            "is_weekend_start": is_weekend_start,
            "discount_pct": discount_pct,
            "total_slots": total_slots,
            "booked_participants": target_demand,
        })

    return rows
