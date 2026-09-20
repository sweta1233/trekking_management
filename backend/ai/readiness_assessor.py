import logging
from typing import Dict, Any, Optional

from models import Trek

logger = logging.getLogger("TMA.ReadinessAssessor")


class ReadinessAssessorService:
    """
    Evaluates cardiovascular, muscular, and altitude fitness preparedness.
    Produces a 6-week progressive conditioning program tailored to trek demands.
    """

    def assess_readiness(
        self,
        user_fitness_level: str = "Moderate",
        weekly_cardio_hours: float = 3.0,
        max_elevation_experience_m: int = 2500,
        target_trek_id: Optional[int] = None,
        target_altitude_m: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Computes fitness readiness score and training roadmap.
        """
        trek_name = "High Altitude Expedition"
        target_altitude = target_altitude_m or 3800
        difficulty = "Moderate"
        duration_days = 5

        if target_trek_id:
            trek = Trek.query.get(target_trek_id)
            if trek:
                trek_name = trek.trek_name
                target_altitude = trek.max_altitude_m
                difficulty = trek.difficulty
                duration_days = trek.duration

        fitness_val_map = {"low": 1.0, "moderate": 2.2, "high": 3.4, "athletic": 4.5}
        fit_score = fitness_val_map.get(user_fitness_level.lower(), 2.0)

        # Calculate demand index based on altitude and difficulty
        difficulty_weight = {"easy": 1.0, "easy to moderate": 1.3, "moderate": 1.8, "difficult": 2.5, "expert": 3.2}
        diff_factor = difficulty_weight.get(difficulty.lower(), 1.8)

        alt_gap = max(0, target_altitude - max_elevation_experience_m)
        alt_demand = (target_altitude / 1000.0) * 1.2 + (alt_gap / 1000.0) * 0.8

        total_demand = diff_factor * 1.5 + alt_demand * 1.2
        user_capacity = fit_score * 1.8 + weekly_cardio_hours * 1.2

        raw_readiness_pct = (user_capacity / max(total_demand, 1.0)) * 100.0
        readiness_pct = min(98, max(25, int(raw_readiness_pct)))

        if readiness_pct >= 80:
            status = "Summit Ready"
            badge_color = "green"
            summary = f"You are well-conditioned for {trek_name}. Maintain current baseline cardio and practice hydration."
        elif readiness_pct >= 55:
            status = "Needs Targeted Conditioning"
            badge_color = "amber"
            summary = f"Good baseline, but you should strengthen uphill stamina and stair-climbing for the {target_altitude}m peak."
        else:
            status = "High Physiological Demand"
            badge_color = "red"
            summary = f"The {target_altitude}m altitude and {difficulty} grade require dedicated endurance training before departure."

        # Generate 6-Week Structured Training Roadmap
        training_weeks = [
            {
                "week_number": "Weeks 1 - 2",
                "phase": "Aerobic Base & Muscular Activation",
                "target": "Build consistent cardiovascular rhythm and joint strength.",
                "schedule": [
                    {"day": "Mon / Wed / Fri", "activity": "30-40 mins steady-state jogging or brisk walking (keep heart rate in Zone 2)."},
                    {"day": "Tue / Thu", "activity": "Bodyweight squats (3x15), forward lunges (3x12), calf raises (3x20), plank hold (3x45s)."},
                    {"day": "Weekend", "activity": "6-8 km nature walk or local hill hike without backpack."},
                ]
            },
            {
                "week_number": "Weeks 3 - 4",
                "phase": "Incline Stamina & Loaded Walking",
                "target": "Simulate alpine gradients and strengthen lower back and glutes.",
                "schedule": [
                    {"day": "Mon / Wed / Fri", "activity": "45 mins stair-climbing or 10-12% treadmill incline walk with 4-5 kg daypack."},
                    {"day": "Tue / Thu", "activity": "Weighted squats, step-ups on 18-inch bench (3x15 per leg), core Russian twists."},
                    {"day": "Weekend", "activity": "10-12 km endurance hike with 5 kg backpack across undulating terrain."},
                ]
            },
            {
                "week_number": "Week 5",
                "phase": "Peak Simulation & Summit Conditioning",
                "target": "Match the physical demands of high-altitude continuous trekking.",
                "schedule": [
                    {"day": "Mon / Wed / Fri", "activity": "5 km interval running (alternate 2 min fast / 1 min jog) + 30 min stair intervals."},
                    {"day": "Tue / Thu", "activity": "Full-body circuit training: Lunges, mountain climbers, pull-ups/push-ups, wall sits."},
                    {"day": "Weekend", "activity": "14-16 km continuous trail hike carrying full 7-8 kg rucksack."},
                ]
            },
            {
                "week_number": "Week 6",
                "phase": "Tapering, Hydration & Mental Preparation",
                "target": "Allow muscle tissue restoration, store glycogen, and prevent pre-trek fatigue.",
                "schedule": [
                    {"day": "Mon - Wed", "activity": "Light 25-minute recovery walks, dynamic stretching, foam rolling."},
                    {"day": "Thu - Sat", "activity": "Rest days: Hydrate with 3-4 liters daily, optimize sleep (8+ hours), finalize gear packing."},
                    {"day": "Departure", "activity": "Arrive fresh, injury-free, and energized for the expedition."},
                ]
            }
        ]

        benchmarks = {
            "target_5k_run_time": "Under 30-33 minutes",
            "daily_stairs_capacity": "45-60 flights continuously",
            "squat_benchmark": "3 sets of 25 bodyweight squats with good form",
            "hydration_target": "4 Litres daily at basecamp and above",
        }

        return {
            "trek_name": trek_name,
            "target_altitude_m": target_altitude,
            "difficulty": difficulty,
            "readiness_percentage": readiness_pct,
            "status": status,
            "badge_color": badge_color,
            "summary": summary,
            "user_metrics": {
                "fitness_level": user_fitness_level,
                "weekly_cardio_hours": weekly_cardio_hours,
                "max_elevation_experience_m": max_elevation_experience_m,
                "elevation_delta_m": alt_gap,
            },
            "benchmarks": benchmarks,
            "training_program": training_weeks,
            "medical_disclaimer": "This fitness evaluation and training roadmap are informational recommendations. Consult a certified physician and conduct an ECG / stress test prior to high-altitude mountaineering.",
        }


# Singleton
_readiness_assessor_instance = None


def get_readiness_assessor() -> ReadinessAssessorService:
    global _readiness_assessor_instance
    if _readiness_assessor_instance is None:
        _readiness_assessor_instance = ReadinessAssessorService()
    return _readiness_assessor_instance
