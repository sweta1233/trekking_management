import logging
from typing import Dict, Any, List, Optional

from models import Trek, ItineraryItem
from ai.llm_provider import get_llm_provider

logger = logging.getLogger("TMA.TripPlanner")


class TripPlannerService:
    """
    Intelligent constraint-aware expedition trip planner.
    Synthesizes realistic alpine itineraries respecting elevation gain gradients
    and acclimatization best practices.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    def generate_itinerary(
        self,
        trek_id: Optional[int] = None,
        custom_days: int = 5,
        altitude_target: int = 3800,
        difficulty: str = "Moderate",
        trek_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds a structured day-by-day expedition plan.
        If trek_id is given and exists in DB with itinerary items, leverages official items.
        Otherwise dynamically synthesizes an acclimatization-grounded plan.
        """
        # Case 1: Known Trek from Database
        if trek_id:
            trek = Trek.query.get(trek_id)
            if trek:
                items = ItineraryItem.query.filter_by(trek_id=trek.id).order_by(ItineraryItem.day_number).all()
                if items:
                    return {
                        "trek_id": trek.id,
                        "trek_name": trek.trek_name,
                        "total_days": len(items),
                        "max_altitude_m": trek.max_altitude_m,
                        "difficulty": trek.difficulty,
                        "region": trek.region,
                        "is_curated": True,
                        "itinerary": [item.to_dict() for item in items],
                        "safety_notes": trek.safety_guidelines or "Acclimatize properly, hydrate 4L/day, carry basic first aid.",
                    }

        # Case 2: Synthesize custom itinerary adhering to high altitude rules
        target_name = trek_name or f"Alpine Summit Expedition ({altitude_target}m)"
        days = max(3, min(14, custom_days))

        itinerary = []
        base_altitude = 2000
        current_altitude = base_altitude
        altitude_step = max(300, int((altitude_target - base_altitude) / max(2, (days - 2))))

        for day in range(1, days + 1):
            if day == 1:
                title = f"Arrival at Base Camp ({base_altitude}m)"
                desc = "Arrive at basecamp, orientation briefing, gear inspection, and evening acclimatization walk."
                start_alt = base_altitude - 200
                end_alt = base_altitude
                dist = 4.0
                hours = 3.0
                stay = "Base Village Guest House / Fixed Alpine Tents"
            elif day == days:
                title = f"Descent & Return to Base Village ({base_altitude}m)"
                desc = "Final descent through pine forests, debriefing session, certificate ceremony, and departure."
                start_alt = current_altitude
                end_alt = base_altitude
                dist = 9.0
                hours = 5.0
                stay = "Departure / Hotel"
            elif day == days - 1:
                # Summit Push Day
                title = f"Summit Push to Peak ({altitude_target}m) & Descent"
                desc = f"Alpine alpine start at 3:30 AM. Climb steady ridgeline to reach {altitude_target}m summit for sunrise. Celebrate panoramic views, descend to intermediate camp."
                start_alt = current_altitude
                end_alt = current_altitude - 400
                dist = 11.5
                hours = 7.5
                stay = "High Campsite (Alpine Tents)"
            else:
                # Progressive Ascent Day
                current_altitude = min(altitude_target - 300, current_altitude + altitude_step)
                title = f"Trek to Camp {day - 1} ({current_altitude}m)"
                desc = f"Moderate gradient trail crossing mountain streams and birch forests. Practice 'climb high, sleep low' acclimatization protocols."
                start_alt = current_altitude - altitude_step
                end_alt = current_altitude
                dist = 7.0
                hours = 5.5
                stay = f"Camp {day - 1} Alpine Meadows"

            itinerary.append({
                "day_number": day,
                "title": title,
                "description": desc,
                "start_altitude_m": start_alt,
                "end_altitude_m": end_alt,
                "distance_km": dist,
                "trekking_time_hours": hours,
                "overnight_stay": stay,
                "meals_included": "Breakfast, Packed Lunch, Hot Dinner",
            })

        return {
            "trek_id": None,
            "trek_name": target_name,
            "total_days": days,
            "max_altitude_m": altitude_target,
            "difficulty": difficulty,
            "region": "Himalayas / High Alpine",
            "is_curated": False,
            "itinerary": itinerary,
            "safety_notes": "Follow 500m daily sleeping altitude gain guidelines above 3000m. Drink 4L of warm fluids daily.",
        }


# Singleton
_trip_planner_instance = None


def get_trip_planner() -> TripPlannerService:
    global _trip_planner_instance
    if _trip_planner_instance is None:
        _trip_planner_instance = TripPlannerService()
    return _trip_planner_instance
