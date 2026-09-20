import logging
from typing import Dict, Any, List, Optional

from models import Trek

logger = logging.getLogger("TMA.PackingAssistant")


class PackingAssistantService:
    """
    Altitude, climate, and duration adaptive packing list generator for mountaineers.
    """

    def generate_checklist(
        self,
        trek_id: Optional[int] = None,
        altitude_m: int = 3800,
        season: str = "Autumn",
        duration_days: int = 5,
        expected_rain: bool = False,
        expected_snow: bool = False,
    ) -> Dict[str, Any]:
        """
        Generates customized gear and packing items organized by category.
        """
        trek_name = "Custom Alpine Trek"
        if trek_id:
            trek = Trek.query.get(trek_id)
            if trek:
                trek_name = trek.trek_name
                altitude_m = trek.max_altitude_m
                duration_days = trek.duration

        is_extreme_altitude = altitude_m >= 4200
        is_high_altitude = altitude_m >= 3200
        is_winter = season.lower() in ["winter", "december", "january", "february"]
        is_monsoon = season.lower() in ["monsoon", "july", "august"] or expected_rain

        categories = []

        # 1. Clothing & Layering System
        clothing = [
            {"item": "Moisture-wicking synthetic t-shirts", "qty": min(4, duration_days - 1), "essential": True, "notes": "Avoid cotton"},
            {"item": "Quick-dry trekking pants", "qty": 2, "essential": True, "notes": "Convertible or stretchable"},
            {"item": "Thermal base layers (top & bottom)", "qty": 2 if is_winter else 1, "essential": is_high_altitude, "notes": "Merino wool or synthetic thermals"},
            {"item": "Fleece jacket (mid-layer)", "qty": 1, "essential": True, "notes": "200-300 GSM warmth"},
            {"item": "Heavy Down Jacket (700+ fill power)", "qty": 1, "essential": is_high_altitude, "notes": f"Rated for -{10 if is_winter or is_extreme_altitude else 5}°C"},
            {"item": "Waterproof / Windproof outer jacket", "qty": 1, "essential": True, "notes": "Gore-Tex or breathable waterproof shell"},
        ]
        categories.append({"name": "Clothing & Layering System", "icon": "shirt", "items": clothing})

        # 2. Footwear & Extremity Protection
        footwear = [
            {"item": "Trekking boots with high ankle support", "qty": 1, "essential": True, "notes": "Broken-in with deep lug Vibram soles"},
            {"item": "Cushioned trekking socks (wool/synthetic)", "qty": min(5, duration_days), "essential": True, "notes": "Always keep 1 dry pair reserved for camp"},
            {"item": "Fleece-lined winter gloves + waterproof outer gloves", "qty": 2, "essential": is_high_altitude, "notes": "Layered hand protection"},
            {"item": "Warm woolen beanie / Balaclava", "qty": 1, "essential": True, "notes": "Full ear protection for summit wind"},
            {"item": "Sun protection cap with neck flap", "qty": 1, "essential": True, "notes": "Essential for sunny valley walks"},
        ]
        if expected_snow or is_winter or is_extreme_altitude:
            footwear.append({"item": "Microspikes & High Gaiters", "qty": 1, "essential": True, "notes": "Prevents snow entering boots & slipping on verglas"})
        categories.append({"name": "Footwear & Extremities", "icon": "boot", "items": footwear})

        # 3. Packs & Technical Trekking Gear
        gear = [
            {"item": f"{'60-70L' if duration_days > 5 else '50-60L'} Rucksack with internal frame", "qty": 1, "essential": True, "notes": "Ensure ergonomic hip belt"},
            {"item": "Waterproof Rucksack Rain Cover", "qty": 1, "essential": True, "notes": "100% waterproof high-vis cover"},
            {"item": "Trekking Poles (Pair with shock absorption)", "qty": 1, "essential": True, "notes": "Reduces 25% knee impact on descent"},
            {"item": "LED Headlamp with extra lithium batteries", "qty": 1, "essential": True, "notes": "For 3 AM summit pushes & camp movement"},
            {"item": "UV400 Category 3/4 Polarized Sunglasses", "qty": 1, "essential": True, "notes": "Crucial to prevent snow blindness"},
        ]
        if is_monsoon:
            gear.append({"item": "Heavy-duty waterproof Poncho / Raincoat", "qty": 1, "essential": True, "notes": "Covers both trekker and daypack"})
        categories.append({"name": "Rucksacks & Technical Hardware", "icon": "backpack", "items": gear})

        # 4. Hydration & Sustenance
        hydration = [
            {"item": "Insulated Thermos flask (1 Litre)", "qty": 1, "essential": True, "notes": "Maintains hot water in sub-zero camps"},
            {"item": "Wide-mouth hydration bottle (1 Litre)", "qty": 1, "essential": True, "notes": "BPA-free durable plastic or aluminum"},
            {"item": "Electrolyte sachets (ORS/Enerzal)", "qty": duration_days * 2, "essential": True, "notes": "Prevents cramping and altitude dehydration"},
            {"item": "High-calorie energy bars, trail mix, dry fruits", "qty": duration_days, "essential": False, "notes": "Fast-absorbing carbs on ascent"},
        ]
        categories.append({"name": "Hydration & Energy", "icon": "bottle", "items": hydration})

        # 5. Medical Kit & Altitude Safety
        medical = [
            {"item": "Diamox (Acetazolamide 125/250mg)", "qty": 10, "essential": is_high_altitude, "notes": "AMS prevention — consult physician first"},
            {"item": "Paracetamol & Ibuprofen", "qty": 1, "essential": True, "notes": "Pain, mild altitude headache, fever"},
            {"item": "Blister prevention tape & sterile Band-Aids", "qty": 10, "essential": True, "notes": "Compeed / Leukotape"},
            {"item": "Antiseptic cream & D-Cold / Cetirizine", "qty": 1, "essential": True, "notes": "Cold / allergy prevention"},
            {"item": "Water purification tablets (Chlorine/Iodine)", "qty": 20, "essential": True, "notes": "For non-boiled natural stream water"},
        ]
        categories.append({"name": "Medical First Aid & Altitude Kit", "icon": "medkit", "items": medical})

        # 6. Personal Hygiene & Eco Ethics
        hygiene = [
            {"item": "High SPF 50+ broad-spectrum sunscreen", "qty": 1, "essential": True, "notes": "UV index is 30% stronger at high altitude"},
            {"item": "Lip balm with SPF 30+", "qty": 1, "essential": True, "notes": "Prevents painful wind-burn and cracked lips"},
            {"item": "Biodegradable toilet paper & wet wipes", "qty": 1, "essential": True, "notes": "Pack out all waste (Leave No Trace)"},
            {"item": "Quick-dry microfiber travel towel", "qty": 1, "essential": True, "notes": "Lightweight & fast drying"},
        ]
        categories.append({"name": "Hygiene & Eco-Trail Essentials", "icon": "sparkles", "items": hygiene})

        # Count totals
        total_items = sum(len(c["items"]) for c in categories)
        essential_items = sum(len([i for i in c["items"] if i["essential"]]) for c in categories)

        return {
            "trek_name": trek_name,
            "altitude_m": altitude_m,
            "season": season,
            "duration_days": duration_days,
            "conditions": {
                "is_high_altitude": is_high_altitude,
                "is_extreme_altitude": is_extreme_altitude,
                "expected_rain": expected_rain,
                "expected_snow": expected_snow,
            },
            "total_items_count": total_items,
            "essential_count": essential_items,
            "categories": categories,
        }


# Singleton
_packing_assistant_instance = None


def get_packing_assistant() -> PackingAssistantService:
    global _packing_assistant_instance
    if _packing_assistant_instance is None:
        _packing_assistant_instance = PackingAssistantService()
    return _packing_assistant_instance
