import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import db, Trek, Booking, User, Review, GuideProfile
from ai.vector_store import get_vector_store

logger = logging.getLogger("TMA.Tools")


def tool_search_treks(
    query: Optional[str] = None,
    difficulty: Optional[str] = None,
    max_altitude: Optional[int] = None,
    max_budget: Optional[float] = None,
    max_duration_days: Optional[int] = None,
    region: Optional[str] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """Search available treks matching specific search filters."""
    q = Trek.query.filter(Trek.status.in_(["Open", "Pending"]))

    if query:
        search_pattern = f"%{query}%"
        q = q.filter(
            (Trek.trek_name.ilike(search_pattern)) |
            (Trek.location.ilike(search_pattern)) |
            (Trek.description.ilike(search_pattern)) |
            (Trek.region.ilike(search_pattern))
        )
    if difficulty:
        q = q.filter(Trek.difficulty.ilike(f"%{difficulty}%"))
    if max_altitude:
        q = q.filter(Trek.max_altitude_m <= max_altitude)
    if max_budget:
        q = q.filter(Trek.price <= max_budget)
    if max_duration_days:
        q = q.filter(Trek.duration <= max_duration_days)
    if region:
        q = q.filter(Trek.region.ilike(f"%{region}%"))

    treks = q.order_by(Trek.rating_avg.desc()).limit(limit).all()

    return {
        "count": len(treks),
        "treks": [t.to_dict() for t in treks],
    }


def tool_get_trek_details(trek_id: int) -> Dict[str, Any]:
    """Retrieve complete database record and day-by-day itinerary of a specific trek."""
    trek = Trek.query.get(trek_id)
    if not trek:
        return {"error": f"Trek with ID {trek_id} not found."}
    return trek.to_dict(include_itinerary=True, include_guide=True)


def tool_search_documents(
    query: str,
    trek_id: Optional[int] = None,
    category: Optional[str] = None,
    top_k: int = 3,
) -> Dict[str, Any]:
    """Perform RAG vector semantic search over official guides and manuals."""
    vs = get_vector_store()
    results = vs.similarity_search(query=query, k=top_k, trek_id=trek_id, category=category)
    return {
        "results_count": len(results),
        "citations": [
            {
                "title": r.get("title"),
                "page": r.get("page_number"),
                "section": r.get("section_header"),
                "score": round(r.get("score", 0), 2),
                "excerpt": r.get("content", "")[:250] + "...",
            }
            for r in results
        ],
        "chunks": results,
    }


def tool_recommend_treks(
    experience_level: str = "Beginner",
    fitness_level: str = "Moderate",
    budget: float = 15000.0,
    preferred_season: Optional[str] = None,
    interests: Optional[str] = None,
    top_n: int = 3,
) -> Dict[str, Any]:
    """Recommend best-matching treks based on user profile and utility scoring."""
    from ai.recommendation_engine import get_recommendation_engine
    engine = get_recommendation_engine()
    return engine.get_recommendations(
        experience_level=experience_level,
        fitness_level=fitness_level,
        budget=budget,
        preferred_season=preferred_season,
        interests=interests,
        top_n=top_n,
    )


def tool_check_availability(trek_id: int) -> Dict[str, Any]:
    """Check open slots, expedition dates, and booking status for a trek."""
    trek = Trek.query.get(trek_id)
    if not trek:
        return {"error": f"Trek {trek_id} not found."}

    return {
        "trek_id": trek.id,
        "trek_name": trek.trek_name,
        "status": trek.status,
        "available_slots": trek.available_slots,
        "total_slots": trek.total_slots,
        "start_date": trek.start_date.isoformat() if trek.start_date else None,
        "end_date": trek.end_date.isoformat() if trek.end_date else None,
        "price_per_person": trek.price,
        "is_bookable": trek.status == "Open" and trek.available_slots > 0,
    }


def tool_get_user_bookings(user_id: int) -> Dict[str, Any]:
    """Retrieve active and historical bookings for a user."""
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
    return {
        "user_id": user_id,
        "count": len(bookings),
        "bookings": [b.to_dict() for b in bookings],
    }


def tool_create_booking(
    user_id: int,
    trek_id: int,
    participants_count: int = 1,
    emergency_name: Optional[str] = None,
    emergency_phone: Optional[str] = None,
    special_requests: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a booking reservation for a trekker."""
    trek = Trek.query.get(trek_id)
    if not trek:
        return {"success": False, "error": f"Trek {trek_id} not found."}

    if trek.status != "Open" or trek.available_slots < participants_count:
        return {
            "success": False,
            "error": f"Insufficient slots available ({trek.available_slots} remaining).",
        }

    total_amount = trek.price * participants_count

    booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        participants_count=participants_count,
        amount=total_amount,
        emergency_contact_name=emergency_name,
        emergency_contact_phone=emergency_phone,
        special_requests=special_requests,
        status="Booked",
        payment_method="Card",
        payment_status="Paid",
    )

    trek.available_slots = max(0, trek.available_slots - participants_count)
    db.session.add(booking)
    db.session.commit()

    return {
        "success": True,
        "booking_id": booking.id,
        "trek_name": trek.trek_name,
        "participants_count": participants_count,
        "total_amount": total_amount,
        "status": booking.status,
        "start_date": trek.start_date.isoformat() if trek.start_date else None,
    }


def tool_generate_itinerary(
    trek_id: Optional[int] = None,
    days: int = 5,
    altitude_target: int = 3800,
    difficulty: str = "Moderate",
    trek_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate altitude-acclimatized day-by-day expedition itinerary."""
    from ai.trip_planner import get_trip_planner
    planner = get_trip_planner()
    return planner.generate_itinerary(
        trek_id=trek_id,
        custom_days=days,
        altitude_target=altitude_target,
        difficulty=difficulty,
        trek_name=trek_name,
    )


def tool_analyze_reviews(trek_id: int) -> Dict[str, Any]:
    """Analyze trekker reviews using aspect-based sentiment analysis."""
    from ai.review_analyzer import get_review_analyzer
    analyzer = get_review_analyzer()
    return analyzer.analyze_trek_reviews(trek_id=trek_id)


def tool_assess_readiness(
    user_fitness_level: str,
    weekly_cardio_hours: float,
    max_elevation_experience_m: int,
    target_trek_id: Optional[int] = None,
    target_altitude_m: Optional[int] = None,
) -> Dict[str, Any]:
    """Assess user physical readiness and produce custom 6-week training roadmap."""
    from ai.readiness_assessor import get_readiness_assessor
    assessor = get_readiness_assessor()
    return assessor.assess_readiness(
        user_fitness_level=user_fitness_level,
        weekly_cardio_hours=weekly_cardio_hours,
        max_elevation_experience_m=max_elevation_experience_m,
        target_trek_id=target_trek_id,
        target_altitude_m=target_altitude_m,
    )


def tool_generate_packing_list(
    trek_id: Optional[int] = None,
    altitude_m: int = 3800,
    season: str = "Autumn",
    duration_days: int = 5,
    expected_rain: bool = False,
    expected_snow: bool = False,
) -> Dict[str, Any]:
    """Generate altitude and weather adaptive packing checklist."""
    from ai.packing_assistant import get_packing_assistant
    assistant = get_packing_assistant()
    return assistant.generate_checklist(
        trek_id=trek_id,
        altitude_m=altitude_m,
        season=season,
        duration_days=duration_days,
        expected_rain=expected_rain,
        expected_snow=expected_snow,
    )
