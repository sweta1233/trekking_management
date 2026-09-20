import json
import logging
import re
import time
from typing import Dict, Any, List, Optional, TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, START, END

from config import Config
from models import db, Conversation, Message, AIInteractionLog, User, Trek
from ai.llm_provider import get_llm_provider
from ai.rag_service import get_rag_service
from ai import tools

logger = logging.getLogger("TMA.AgentGraph")


class AgentState(TypedDict):
    user_id: Optional[int]
    session_id: str
    user_query: str
    conversation_history: List[Dict[str, str]]
    selected_trek_id: Optional[int]
    user_profile: Dict[str, Any]

    # Graph Execution State
    classified_intent: str
    tool_calls: List[Dict[str, Any]]
    retrieved_sources: List[Dict[str, Any]]
    intermediate_data: Dict[str, Any]
    generated_response: str
    grounding_score: float
    safety_check_passed: bool
    latency_ms: int
    model_used: str
    prompt_tokens: int
    completion_tokens: int


class TrekMateAgentWorkflow:
    """
    LangGraph-powered stateful multi-agent system for TrekMate AI.
    Implements Intent Classification -> Dynamic Routing -> Specialized Sub-Agents
    -> Grounded Response Synthesis -> Safety Validation.
    """

    def __init__(self):
        self.llm = get_llm_provider()
        self.rag = get_rag_service()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Register Nodes
        workflow.add_node("intent_classifier", self._node_classify_intent)
        workflow.add_node("recommendation_agent", self._node_recommendation_agent)
        workflow.add_node("rag_information_agent", self._node_rag_information_agent)
        workflow.add_node("trip_planning_agent", self._node_trip_planning_agent)
        workflow.add_node("booking_agent", self._node_booking_agent)
        workflow.add_node("fitness_readiness_agent", self._node_fitness_agent)
        workflow.add_node("packing_agent", self._node_packing_agent)
        workflow.add_node("review_analytics_agent", self._node_review_agent)
        workflow.add_node("general_assistant", self._node_general_assistant)
        workflow.add_node("response_generator", self._node_response_generator)
        workflow.add_node("safety_grounding_validator", self._node_safety_validator)

        # Define Edges & Conditional Routing
        workflow.add_edge(START, "intent_classifier")

        workflow.add_conditional_edges(
            "intent_classifier",
            self._route_by_intent,
            {
                "recommendation": "recommendation_agent",
                "rag": "rag_information_agent",
                "trip_planning": "trip_planning_agent",
                "booking": "booking_agent",
                "fitness": "fitness_readiness_agent",
                "packing": "packing_agent",
                "reviews": "review_analytics_agent",
                "general": "general_assistant",
            }
        )

        # Join sub-agents into response generator
        workflow.add_edge("recommendation_agent", "response_generator")
        workflow.add_edge("rag_information_agent", "response_generator")
        workflow.add_edge("trip_planning_agent", "response_generator")
        workflow.add_edge("booking_agent", "response_generator")
        workflow.add_edge("fitness_readiness_agent", "response_generator")
        workflow.add_edge("packing_agent", "response_generator")
        workflow.add_edge("review_analytics_agent", "response_generator")
        workflow.add_edge("general_assistant", "response_generator")

        workflow.add_edge("response_generator", "safety_grounding_validator")
        workflow.add_edge("safety_grounding_validator", END)

        return workflow.compile()

    # --- Node Implementations ---

    def _node_classify_intent(self, state: AgentState) -> Dict[str, Any]:
        """Classifies the user's intent based on text and conversational context."""
        query = state["user_query"].lower()

        # Rule & Keyword heuristic classifier
        if any(k in query for k in ["recommend", "suggest", "which trek", "beginner trek", "best trek for", "find me a trek"]):
            intent = "recommendation"
        elif any(k in query for k in ["pack", "gear", "equipment", "clothes", "checklist", "what to wear", "shoes", "down jacket"]):
            intent = "packing"
        elif any(k in query for k in ["fitness", "readiness", "train", "workout", "stamina", "prepare for", "can i do", "endurance"]):
            intent = "fitness"
        elif any(k in query for k in ["itinerary", "day 1", "day by day", "how many days", "plan trip", "schedule", "route plan"]):
            intent = "trip_planning"
        elif any(k in query for k in ["book", "reserve", "slot", "payment", "my booking", "cancel booking", "ticket"]):
            intent = "booking"
        elif any(k in query for k in ["review", "feedback", "rating", "experience of others", "what people say"]):
            intent = "reviews"
        elif any(k in query for k in ["altitude", "safety", "permit", "acclimatization", "guide", "rule", "document", "route", "weather", "ams", "diamox", "emergency", "kedarkantha", "hampta", "valley of flowers", "brahmatal", "chadar"]):
            intent = "rag"
        else:
            intent = "general"

        return {
            "classified_intent": intent,
            "tool_calls": state.get("tool_calls", []),
            "retrieved_sources": state.get("retrieved_sources", []),
            "intermediate_data": {},
        }

    def _route_by_intent(self, state: AgentState) -> str:
        return state.get("classified_intent", "general")

    def _node_recommendation_agent(self, state: AgentState) -> Dict[str, Any]:
        profile = state.get("user_profile", {})
        res = tools.tool_recommend_treks(
            experience_level=profile.get("experience_level", "Beginner"),
            fitness_level=profile.get("fitness_level", "Moderate"),
            budget=profile.get("budget_preference", 18000.0),
            preferred_season="Autumn",
            interests=state["user_query"],
            top_n=3,
        )
        tool_call = {
            "tool": "recommend_treks",
            "params": {"query": state["user_query"], "user_profile": profile},
            "result_summary": f"Found {res.get('count', 0)} matching expeditions.",
        }
        return {
            "intermediate_data": {"recommendation_result": res},
            "tool_calls": state.get("tool_calls", []) + [tool_call],
        }

    def _node_rag_information_agent(self, state: AgentState) -> Dict[str, Any]:
        rag_res = self.rag.generate_grounded_answer(
            user_query=state["user_query"],
            trek_id=state.get("selected_trek_id"),
        )
        tool_call = {
            "tool": "search_documents",
            "params": {"query": state["user_query"], "trek_id": state.get("selected_trek_id")},
            "result_summary": f"Retrieved {rag_res.get('retrieval_count', 0)} verified chunks with citations.",
        }
        return {
            "intermediate_data": {"rag_result": rag_res},
            "retrieved_sources": rag_res.get("sources", []),
            "grounding_score": rag_res.get("grounding_score", 0.95),
            "tool_calls": state.get("tool_calls", []) + [tool_call],
        }

    def _node_trip_planning_agent(self, state: AgentState) -> Dict[str, Any]:
        trek_id = state.get("selected_trek_id")
        plan_res = tools.tool_generate_itinerary(
            trek_id=trek_id,
            days=5,
            altitude_target=3800,
            difficulty="Moderate",
        )
        tool_call = {
            "tool": "generate_itinerary",
            "params": {"trek_id": trek_id, "days": 5},
            "result_summary": f"Generated {plan_res.get('total_days', 5)}-day acclimatization itinerary.",
        }
        return {
            "intermediate_data": {"itinerary_result": plan_res},
            "tool_calls": state.get("tool_calls", []) + [tool_call],
        }

    def _node_booking_agent(self, state: AgentState) -> Dict[str, Any]:
        user_id = state.get("user_id")
        trek_id = state.get("selected_trek_id")

        if "my booking" in state["user_query"].lower() and user_id:
            res = tools.tool_get_user_bookings(user_id)
            tool_name = "get_user_bookings"
        elif trek_id:
            res = tools.tool_check_availability(trek_id)
            tool_name = "check_availability"
        else:
            res = tools.tool_search_treks(limit=3)
            tool_name = "search_treks"

        tool_call = {
            "tool": tool_name,
            "params": {"user_id": user_id, "trek_id": trek_id},
            "result_summary": "Retrieved booking and availability status.",
        }
        return {
            "intermediate_data": {"booking_result": res},
            "tool_calls": state.get("tool_calls", []) + [tool_call],
        }

    def _node_fitness_agent(self, state: AgentState) -> Dict[str, Any]:
        profile = state.get("user_profile", {})
        res = tools.tool_assess_readiness(
            user_fitness_level=profile.get("fitness_level", "Moderate"),
            weekly_cardio_hours=3.5,
            max_elevation_experience_m=profile.get("max_altitude_climbed", 2500),
            target_trek_id=state.get("selected_trek_id"),
        )
        tool_call = {
            "tool": "assess_readiness",
            "params": {"user_fitness": profile.get("fitness_level"), "trek_id": state.get("selected_trek_id")},
            "result_summary": f"Readiness computed at {res.get('readiness_percentage')}% ({res.get('status')}).",
        }
        return {
            "intermediate_data": {"readiness_result": res},
            "tool_calls": state.get("tool_calls", []) + [tool_call],
        }

    def _node_packing_agent(self, state: AgentState) -> Dict[str, Any]:
        trek_id = state.get("selected_trek_id")
        res = tools.tool_generate_packing_list(
            trek_id=trek_id,
            altitude_m=3800,
            season="Autumn",
            duration_days=5,
        )
        tool_call = {
            "tool": "generate_packing_list",
            "params": {"trek_id": trek_id, "altitude_m": 3800},
            "result_summary": f"Generated checklist of {res.get('total_items_count')} items across {len(res.get('categories', []))} categories.",
        }
        return {
            "intermediate_data": {"packing_result": res},
            "tool_calls": state.get("tool_calls", []) + [tool_call],
        }

    def _node_review_agent(self, state: AgentState) -> Dict[str, Any]:
        trek_id = state.get("selected_trek_id") or 1
        res = tools.tool_analyze_reviews(trek_id=trek_id)
        tool_call = {
            "tool": "analyze_reviews",
            "params": {"trek_id": trek_id},
            "result_summary": f"Aspect sentiment analyzed for {res.get('trek_name', 'Trek')} ({res.get('overall_sentiment')}).",
        }
        return {
            "intermediate_data": {"review_result": res},
            "tool_calls": state.get("tool_calls", []) + [tool_call],
        }

    def _node_general_assistant(self, state: AgentState) -> Dict[str, Any]:
        system_prompt = (
            "You are TrekMate AI, the intelligent mountaineering and adventure assistant.\n"
            "Provide helpful, concise, and structured guidance on trekking destinations, trail etiquette, "
            "Leave No Trace principles, high altitude safety, and gear requirements."
        )
        messages = state.get("conversation_history", []) + [{"role": "user", "content": state["user_query"]}]
        res = self.llm.generate_chat_response(messages=messages, system_prompt=system_prompt)
        return {
            "intermediate_data": {"direct_llm_response": res.get("content")},
            "model_used": res.get("model", "mock"),
            "prompt_tokens": res.get("prompt_tokens", 0),
            "completion_tokens": res.get("completion_tokens", 0),
        }

    def _node_response_generator(self, state: AgentState) -> Dict[str, Any]:
        """Synthesizes structured, rich markdown from intermediate sub-agent outputs."""
        intent = state.get("classified_intent")
        data = state.get("intermediate_data", {})

        if intent == "rag" and "rag_result" in data:
            response = data["rag_result"].get("answer", "")
        elif intent == "recommendation" and "recommendation_result" in data:
            recs = data["recommendation_result"].get("recommendations", [])
            lines = ["Here are the top trek recommendations tailored to your profile:\n"]
            for i, r in enumerate(recs, 1):
                t = r["trek"]
                lines.append(f"**{i}. {t['trek_name']} ({t['max_altitude_m']}m)** — `{t['difficulty']}` | {t['duration']} Days | ₹{int(t['price']):,}")
                lines.append(f"   - *Match Score*: **{r['match_score']}%**")
                for reason in r.get("match_reasons", [])[:2]:
                    lines.append(f"   - ✓ {reason}")
                lines.append("")
            lines.append("Would you like to explore full day-by-day itineraries or check gear checklists for any of these?")
            response = "\n".join(lines)
        elif intent == "trip_planning" and "itinerary_result" in data:
            plan = data["itinerary_result"]
            lines = [f"### 🏔️ Expedition Itinerary: {plan.get('trek_name')}\n"]
            lines.append(f"**Duration**: {plan.get('total_days')} Days | **Max Altitude**: {plan.get('max_altitude_m')}m | **Grade**: {plan.get('difficulty')}\n")
            for item in plan.get("itinerary", []):
                lines.append(f"**Day {item['day_number']}: {item['title']}**")
                lines.append(f"• *Elevation*: {item.get('start_altitude_m', 2000)}m → {item.get('end_altitude_m', 2500)}m | *Distance*: {item.get('distance_km', 5)} km ({item.get('trekking_time_hours', 4)} hrs)")
                lines.append(f"• *Details*: {item.get('description')}")
                lines.append(f"• *Night Stay*: {item.get('overnight_stay', 'Alpine Campsite')}\n")
            lines.append(f"⚠️ **Safety Note**: {plan.get('safety_notes')}")
            response = "\n".join(lines)
        elif intent == "fitness" and "readiness_result" in data:
            fit = data["readiness_result"]
            lines = [f"### 🏃 Trek Readiness Assessment: {fit.get('trek_name')}\n"]
            lines.append(f"• **Readiness Score**: **{fit.get('readiness_percentage')}%** (`{fit.get('status')}`)")
            lines.append(f"• **Evaluation Summary**: {fit.get('summary')}\n")
            lines.append("#### 6-Week Progressive Conditioning Phases:")
            for prog in fit.get("training_program", []):
                lines.append(f"**{prog['week_number']}: {prog['phase']}**")
                lines.append(f"*{prog['target']}*")
                for s in prog.get("schedule", []):
                    lines.append(f"  - **{s['day']}**: {s['activity']}")
                lines.append("")
            lines.append(f"⚠️ *{fit.get('medical_disclaimer')}*")
            response = "\n".join(lines)
        elif intent == "packing" and "packing_result" in data:
            pack = data["packing_result"]
            lines = [f"### 🎒 Packing Checklist: {pack.get('trek_name')} ({pack.get('altitude_m')}m)\n"]
            lines.append(f"**Season**: {pack.get('season')} | **Duration**: {pack.get('duration_days')} Days | **Total Items**: {pack.get('total_items_count')} ({pack.get('essential_count')} Essential)\n")
            for cat in pack.get("categories", []):
                lines.append(f"**{cat['name']}**:")
                for item in cat.get("items", []):
                    req_tag = "🔴 [Mandatory]" if item.get("essential") else "⚪ [Recommended]"
                    lines.append(f"• {req_tag} **{item['item']}** (Qty: {item.get('qty', 1)}) — *{item.get('notes', '')}*")
                lines.append("")
            response = "\n".join(lines)
        elif intent == "reviews" and "review_result" in data:
            rev = data["review_result"]
            lines = [f"### 🌟 Review & Sentiment Insights: {rev.get('trek_name')}\n"]
            lines.append(f"• **Average Rating**: {rev.get('average_rating')}/5.0 based on {rev.get('total_reviews')} reviews")
            lines.append(f"• **Overall Trekker Sentiment**: `{rev.get('overall_sentiment')}`\n")
            lines.append("**Aspect Breakdown**:")
            for asp, score in rev.get("aspect_summary", {}).items():
                lines.append(f"  - **{asp.replace('_', ' ').capitalize()}**: `{score}%` positive sentiment")
            lines.append("\n**Key Trekker Highlights**:")
            for h in rev.get("key_strengths", []):
                lines.append(f"  - ✓ {h}")
            response = "\n".join(lines)
        elif intent == "booking" and "booking_result" in data:
            bk = data["booking_result"]
            if "bookings" in bk:
                lines = ["### 🎫 Your Confirmed Trek Bookings:\n"]
                if not bk["bookings"]:
                    lines.append("You currently have no active trek reservations. Browse open treks to plan your adventure!")
                for b in bk["bookings"]:
                    lines.append(f"• **{b.get('trek_name')}** | Status: `{b.get('status')}` | Slots: {b.get('participants_count')} | Paid: ₹{int(b.get('amount', 0)):,}")
                response = "\n".join(lines)
            elif "is_bookable" in bk:
                status_str = "Available for Booking" if bk["is_bookable"] else "Slots Full / Closed"
                response = (
                    f"### 📅 Trek Availability Status: **{bk.get('trek_name')}**\n\n"
                    f"• **Status**: `{status_str}`\n"
                    f"• **Remaining Slots**: **{bk.get('available_slots')}** of {bk.get('total_slots')}\n"
                    f"• **Dates**: {bk.get('start_date')} to {bk.get('end_date')}\n"
                    f"• **Price**: ₹{int(bk.get('price_per_person', 0)):,} per person\n\n"
                    "You can confirm this booking in the Trekker Portal anytime."
                )
            else:
                response = "Trek slots and schedules are updated live. Let me know which trek you'd like to book."
        else:
            response = data.get("direct_llm_response", "I am here to assist your mountain expedition. How can I help?")

        return {"generated_response": response}

    def _node_safety_validator(self, state: AgentState) -> Dict[str, Any]:
        """Validates that high altitude advice contains necessary safety caveats."""
        response = state.get("generated_response", "")
        query = state["user_query"].lower()

        is_high_alt_topic = any(k in query for k in ["altitude", "summit", "ams", "3000m", "4000m", "5000m", "fitness", "pass", "peak"])
        has_safety_note = any(k in response.lower() for k in ["safety", "acclimatiz", "ams", "hydrate", "doctor", "medical", "first aid"])

        if is_high_alt_topic and not has_safety_note:
            response += "\n\n💡 *Mountain Safety Tip: For any trek above 3,000m, always follow conservative ascent rates and stay hydrated with 4L of fluids daily.*"

        return {
            "generated_response": response,
            "safety_check_passed": True,
        }

    # --- Main Execution Entrypoint ---

    def execute_flow(
        self,
        user_id: Optional[int],
        session_id: str,
        user_query: str,
        selected_trek_id: Optional[int] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the LangGraph workflow and records conversation + telemetry.
        """
        start_time = time.time()

        # Load user profile if user_id is provided
        user_profile = {}
        if user_id:
            u = User.query.get(user_id)
            if u:
                user_profile = u.to_dict()

        initial_state: AgentState = {
            "user_id": user_id,
            "session_id": session_id,
            "user_query": user_query,
            "conversation_history": conversation_history or [],
            "selected_trek_id": selected_trek_id,
            "user_profile": user_profile,
            "classified_intent": "general",
            "tool_calls": [],
            "retrieved_sources": [],
            "intermediate_data": {},
            "generated_response": "",
            "grounding_score": 1.0,
            "safety_check_passed": True,
            "latency_ms": 0,
            "model_used": "trekmate-agent-v1",
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }

        try:
            final_state = self.graph.invoke(initial_state)
        except Exception as e:
            logger.error(f"LangGraph execution error: {e}", exc_info=True)
            # Graceful recovery
            final_state = initial_state
            final_state["generated_response"] = (
                f"I processed your query regarding high-altitude trekking. "
                f"Here are key recommendations: prioritize acclimatization, maintain hydration, and verify gear requirements."
            )
            final_state["classified_intent"] = "general"

        latency_ms = int((time.time() - start_time) * 1000)
        final_state["latency_ms"] = latency_ms

        # Persist conversation message and telemetry log
        self._persist_interaction(final_state)

        return {
            "response": final_state.get("generated_response"),
            "intent": final_state.get("classified_intent"),
            "sources": final_state.get("retrieved_sources", []),
            "tool_calls": final_state.get("tool_calls", []),
            "grounding_score": final_state.get("grounding_score", 1.0),
            "safety_checked": final_state.get("safety_check_passed", True),
            "latency_ms": latency_ms,
            "model_used": final_state.get("model_used", "trekmate-agent-v1"),
        }

    def _persist_interaction(self, state: AgentState):
        """Stores conversation turns and observability records in DB."""
        try:
            user_id = state.get("user_id")
            session_id = state.get("session_id")
            if not session_id:
                return

            # Find or create conversation
            conv = Conversation.query.filter_by(session_id=session_id).first()
            if not conv and user_id:
                conv = Conversation(
                    user_id=user_id,
                    session_id=session_id,
                    title=state.get("user_query")[:40] + "...",
                    selected_trek_id=state.get("selected_trek_id"),
                )
                db.session.add(conv)
                db.session.commit()

            if conv:
                # Add User message
                msg_user = Message(
                    conversation_id=conv.id,
                    role="user",
                    content=state.get("user_query"),
                    intent=state.get("classified_intent"),
                )
                db.session.add(msg_user)

                # Add Assistant message
                msg_assistant = Message(
                    conversation_id=conv.id,
                    role="assistant",
                    content=state.get("generated_response"),
                    intent=state.get("classified_intent"),
                    sources=json.dumps(state.get("retrieved_sources", [])),
                    tool_calls=json.dumps(state.get("tool_calls", [])),
                    latency_ms=state.get("latency_ms", 0),
                )
                db.session.add(msg_assistant)
                db.session.commit()

            # Record Observability Log
            log = AIInteractionLog(
                user_id=user_id,
                session_id=session_id,
                request_type=state.get("classified_intent", "chat"),
                model_used=state.get("model_used", "trekmate-agent-v1"),
                prompt_tokens=state.get("prompt_tokens", len(state.get("user_query", "")) // 4),
                completion_tokens=state.get("completion_tokens", len(state.get("generated_response", "")) // 4),
                latency_ms=state.get("latency_ms", 0),
                tool_used=",".join([tc.get("tool", "") for tc in state.get("tool_calls", [])]) if state.get("tool_calls") else None,
                retrieval_count=len(state.get("retrieved_sources", [])),
                grounding_score=state.get("grounding_score", 1.0),
                was_safe=state.get("safety_check_passed", True),
            )
            db.session.add(log)
            db.session.commit()

        except Exception as e:
            logger.warning(f"Failed to persist agent interaction: {e}")
            db.session.rollback()


# Singleton
_agent_workflow_instance = None


def get_agent_workflow() -> TrekMateAgentWorkflow:
    global _agent_workflow_instance
    if _agent_workflow_instance is None:
        _agent_workflow_instance = TrekMateAgentWorkflow()
    return _agent_workflow_instance
