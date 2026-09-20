import logging
import json
from typing import List, Dict, Any, Optional
import numpy as np

from models import Trek, User
from ai.embeddings import get_embedding_provider

logger = logging.getLogger("TMA.RecommendationEngine")


class TrekRecommendationEngine:
    """
    Multi-factor utility scoring and semantic matching recommendation engine
    with explainable match reasoning.
    """

    def __init__(self):
        self.embedder = get_embedding_provider()

    def get_recommendations(
        self,
        experience_level: str = "Beginner",
        fitness_level: str = "Moderate",
        budget: float = 20000.0,
        preferred_season: Optional[str] = None,
        interests: Optional[str] = None,
        max_duration_days: Optional[int] = None,
        max_altitude_climbed: int = 2500,
        top_n: int = 4,
    ) -> Dict[str, Any]:
        """
        Computes composite utility scores for all active treks in database.
        """
        all_treks = Trek.query.filter(Trek.status.in_(["Open", "Pending"])).all()
        if not all_treks:
            return {"recommendations": [], "count": 0, "status": "no_treks"}

        user_query_text = f"{experience_level} {fitness_level} {interests or 'mountain scenic pass'} {preferred_season or ''}"
        query_vector = np.array(self.embedder.embed_query(user_query_text), dtype=np.float32)

        scored_treks = []

        for trek in all_treks:
            # 1. Experience & Difficulty Fit (Weight: 25%)
            diff_score, diff_reason = self._score_difficulty(experience_level, trek.difficulty)

            # 2. Altitude Safety & Fitness Fit (Weight: 25%)
            alt_score, alt_reason = self._score_altitude(fitness_level, max_altitude_climbed, trek.max_altitude_m)

            # 3. Budget Fit (Weight: 20%)
            budget_score, budget_reason = self._score_budget(budget, trek.price)

            # 4. Season & Duration Fit (Weight: 15%)
            season_score, season_reason = self._score_season_and_duration(preferred_season, trek.best_season, max_duration_days, trek.duration)

            # 5. Semantic Interest Similarity (Weight: 15%)
            trek_text = f"{trek.trek_name} {trek.location} {trek.description} {trek.highlights} {trek.region}"
            trek_vector = np.array(self.embedder.embed_query(trek_text), dtype=np.float32)
            sim_score = float(np.dot(query_vector, trek_vector))
            sim_score = max(0.0, min(1.0, (sim_score + 1.0) / 2.0))
            sim_reason = f"Matches your interest profile ({int(sim_score * 100)}% semantic affinity)"

            # Composite Score (0.0 to 1.0)
            composite = (
                diff_score * 0.25 +
                alt_score * 0.25 +
                budget_score * 0.20 +
                season_score * 0.15 +
                sim_score * 0.15
            )

            # Boost slightly by rating
            rating_boost = (trek.rating_avg or 4.5) / 5.0 * 0.05
            final_score = min(1.0, round(composite + rating_boost, 3))

            reasons = [r for r in [diff_reason, alt_reason, budget_reason, season_reason, sim_reason] if r]

            scored_treks.append({
                "trek": trek.to_dict(),
                "match_score": int(final_score * 100),
                "utility_breakdown": {
                    "difficulty_fit": int(diff_score * 100),
                    "altitude_fitness_fit": int(alt_score * 100),
                    "budget_fit": int(budget_score * 100),
                    "season_duration_fit": int(season_score * 100),
                    "interest_similarity": int(sim_score * 100),
                },
                "match_reasons": reasons,
            })

        # Sort by match score descending
        scored_treks.sort(key=lambda x: x["match_score"], reverse=True)
        top_results = scored_treks[:top_n]

        return {
            "count": len(top_results),
            "recommendations": top_results,
            "user_criteria": {
                "experience_level": experience_level,
                "fitness_level": fitness_level,
                "budget": budget,
                "preferred_season": preferred_season,
                "interests": interests,
            },
        }

    def _score_difficulty(self, user_exp: str, trek_diff: str) -> tuple[float, str]:
        user_exp = (user_exp or "Beginner").lower()
        trek_diff = (trek_diff or "Moderate").lower()

        hierarchy = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        trek_h = {"easy": 1, "easy to moderate": 1.5, "moderate": 2, "difficult": 3, "expert": 4}

        u_val = hierarchy.get(user_exp, 1)
        t_val = trek_h.get(trek_diff, 2)

        if u_val >= t_val:
            return 1.0, f"Perfect fit for your {user_exp.capitalize()} experience level"
        elif u_val + 0.5 >= t_val:
            return 0.75, f"Moderate challenge suitable for progressing {user_exp.capitalize()} trekkers"
        else:
            return 0.40, f"Demanding trail exceeding standard {user_exp.capitalize()} baseline"

    def _score_altitude(self, fitness: str, max_climbed: int, trek_alt: int) -> tuple[float, str]:
        fitness = (fitness or "Moderate").lower()
        alt_gain = trek_alt - max_climbed

        if trek_alt <= 3000:
            return 1.0, f"Safe altitude ({trek_alt}m) with minimal acute mountain sickness (AMS) risk"
        elif alt_gain <= 800:
            return 0.90, f"Well within your acclimated altitude threshold ({trek_alt}m)"
        elif alt_gain <= 1500 and fitness in ["high", "athletic", "moderate"]:
            return 0.70, f"Altitude step-up ({trek_alt}m) manageable with steady hydration"
        else:
            return 0.45, f"High altitude summit ({trek_alt}m) requires prior acclimatization conditioning"

    def _score_budget(self, user_budget: float, trek_price: float) -> tuple[float, str]:
        if user_budget <= 0:
            return 0.8, "Affordable expedition pricing"

        if trek_price <= user_budget:
            savings = user_budget - trek_price
            return 1.0, f"Under budget by ₹{int(savings):,} (Cost: ₹{int(trek_price):,})"
        elif trek_price <= user_budget * 1.2:
            return 0.65, f"Slightly above target budget (Cost: ₹{int(trek_price):,})"
        else:
            return 0.30, f"Significantly above specified budget limit"

    def _score_season_and_duration(self, user_season: Optional[str], trek_season: str, max_days: Optional[int], trek_days: int) -> tuple[float, str]:
        score = 0.8
        reason = f"Ideal duration of {trek_days} days"

        if max_days and trek_days > max_days:
            score -= 0.3
            reason = f"Exceeds preferred duration ({trek_days} vs {max_days} days)"

        if user_season and user_season.lower() in (trek_season or "").lower():
            score = min(1.0, score + 0.2)
            reason += f" & matches best seasonal window ({trek_season})"

        return max(0.2, score), reason


# Singleton
_rec_engine_instance = None


def get_recommendation_engine() -> TrekRecommendationEngine:
    global _rec_engine_instance
    if _rec_engine_instance is None:
        _rec_engine_instance = TrekRecommendationEngine()
    return _rec_engine_instance
