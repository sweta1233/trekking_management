"""
TrekMate AI API Routes
Comprehensive AI endpoints leveraging RAG, Vector DB, LangChain, LangGraph,
Embeddings, Traditional ML, and intelligent agent orchestration.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename

from models import (
    db, User, Trek, Booking, TrekDocument, DocumentChunk,
    Review, Conversation, Message, AIInteractionLog,
    TrekRecommendationLog
)
from config import Config

# Import AI Services
from ai.agent_graph import get_agent_workflow
from ai.rag_service import get_rag_service
from ai.recommendation_engine import RecommendationEngine
from ai.trip_planner import TripPlannerAgent
from ai.packing_assistant import PackingAssistant
from ai.readiness_assessor import ReadinessAssessor
from ai.review_analyzer import ReviewAnalyzerAgent
from ai.vector_store import get_vector_store
from ai.embeddings import get_embedding_service

# Import ML Services
from ml.demand_model import DemandPredictor

logger = logging.getLogger("TMA.AI_Routes")

ai_api = Blueprint("ai_api", __name__, url_prefix="/api/ai")


# ============================================================================
# AI CHAT ENDPOINT - LangGraph Multi-Agent Orchestration
# ============================================================================

@ai_api.route("/chat", methods=["POST"])
@jwt_required()
def ai_chat():
    """
    Main TrekMate AI chat endpoint using LangGraph multi-agent workflow.

    Routes queries intelligently through:
    - Intent Classifier
    - RAG Information Agent (vector search + document retrieval)
    - Recommendation Agent (embeddings + semantic matching)
    - Trip Planning Agent
    - Booking Agent
    - Fitness/Readiness Agent
    - Packing Assistant Agent
    - Review Analytics Agent
    - General Assistant

    Returns grounded, source-cited responses with safety validation.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    user_query = data.get("message", "").strip()
    session_id = data.get("session_id") or f"session_{user_id}_{int(time.time())}"
    trek_id = data.get("trek_id")

    if not user_query:
        return jsonify({"error": "message is required"}), 400

    try:
        # Execute LangGraph Workflow
        agent_workflow = get_agent_workflow()

        # Load conversation history (last 5 turns for context)
        conv = Conversation.query.filter_by(session_id=session_id).first()
        conversation_history = []
        if conv:
            messages = Message.query.filter_by(conversation_id=conv.id).order_by(Message.id.desc()).limit(10).all()
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in reversed(messages)
            ]

        result = agent_workflow.execute_flow(
            user_id=user_id,
            session_id=session_id,
            user_query=user_query,
            selected_trek_id=trek_id,
            conversation_history=conversation_history,
        )

        return jsonify({
            "response": result.get("response"),
            "session_id": session_id,
            "intent": result.get("intent"),
            "sources": result.get("sources", []),
            "tool_calls": result.get("tool_calls", []),
            "grounding_score": result.get("grounding_score", 1.0),
            "safety_checked": result.get("safety_checked", True),
            "latency_ms": result.get("latency_ms", 0),
            "model_used": result.get("model_used"),
        }), 200

    except Exception as e:
        logger.error(f"AI Chat error: {e}", exc_info=True)
        return jsonify({
            "error": "AI service temporarily unavailable",
            "detail": str(e),
            "fallback_response": "I'm here to help with your trekking adventure. Could you rephrase your question?"
        }), 500


# ============================================================================
# RAG QUERY ENDPOINT - Document Retrieval with Vector Search
# ============================================================================

@ai_api.route("/rag/query", methods=["POST"])
@jwt_required()
def rag_query():
    """
    RAG (Retrieval-Augmented Generation) endpoint.

    Pipeline:
    1. User query -> Embeddings (sentence-transformers/OpenAI)
    2. Vector similarity search in FAISS
    3. Retrieve top-k relevant document chunks
    4. LangChain text splitting & metadata enrichment
    5. LLM synthesis with source citations
    6. Grounding validation

    Returns answer + document sources with page numbers.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    query = data.get("question", "").strip()
    trek_id = data.get("trek_id")
    category = data.get("category")  # route_guide, safety, permits, etc.

    if not query:
        return jsonify({"error": "question is required"}), 400

    try:
        rag_service = get_rag_service()

        result = rag_service.generate_grounded_answer(
            user_query=query,
            trek_id=trek_id,
            category=category,
        )

        # Log interaction
        log = AIInteractionLog(
            user_id=user_id,
            request_type="rag",
            model_used=result.get("model_used"),
            prompt_tokens=result.get("prompt_tokens", 0),
            completion_tokens=result.get("completion_tokens", 0),
            latency_ms=result.get("latency_ms", 0),
            retrieval_count=result.get("retrieval_count", 0),
            grounding_score=result.get("grounding_score", 1.0),
            was_safe=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            "answer": result.get("answer"),
            "sources": result.get("sources", []),
            "retrieval_count": result.get("retrieval_count", 0),
            "grounding_score": result.get("grounding_score", 1.0),
            "model_used": result.get("model_used"),
            "latency_ms": result.get("latency_ms", 0),
        }), 200

    except Exception as e:
        logger.error(f"RAG query error: {e}", exc_info=True)
        return jsonify({
            "error": "RAG service error",
            "detail": str(e)
        }), 500


# ============================================================================
# TREK RECOMMENDATION ENGINE - Embeddings + Semantic Matching
# ============================================================================

@ai_api.route("/recommend", methods=["POST"])
@jwt_required()
def recommend_treks():
    """
    Personalized trek recommendation using:
    - User profile embeddings
    - Trek description embeddings
    - Semantic similarity matching (cosine similarity)
    - Rule-based filtering (budget, difficulty, altitude)
    - Hybrid scoring system

    Returns ranked recommendations with match explanations.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        engine = RecommendationEngine()

        # Extract preferences
        preferences = {
            "experience_level": data.get("experience_level") or user.experience_level,
            "fitness_level": data.get("fitness_level") or user.fitness_level,
            "budget": data.get("budget") or user.budget_preference,
            "max_altitude": data.get("max_altitude") or user.max_altitude_climbed,
            "preferred_difficulty": data.get("preferred_difficulty") or user.preferred_difficulty,
            "duration_days": data.get("duration_days"),
            "season": data.get("season", "Autumn"),
            "interests": data.get("interests", ""),
        }

        top_n = data.get("top_n", 5)

        result = engine.recommend_treks(
            user_profile=preferences,
            top_n=top_n,
        )

        # Log recommendation
        rec_log = TrekRecommendationLog(
            user_id=user_id,
            preferences=json.dumps(preferences),
            recommended_trek_ids=json.dumps([r["trek"]["id"] for r in result.get("recommendations", [])]),
            scores=json.dumps({r["trek"]["id"]: r["match_score"] for r in result.get("recommendations", [])}),
            match_reasons=json.dumps({r["trek"]["id"]: r["match_reasons"] for r in result.get("recommendations", [])}),
        )
        db.session.add(rec_log)
        db.session.commit()

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        return jsonify({
            "error": "Recommendation service error",
            "detail": str(e)
        }), 500


# ============================================================================
# TRIP PLANNER - AI-Generated Itineraries
# ============================================================================

@ai_api.route("/trip-planner", methods=["POST"])
@jwt_required()
def plan_trip():
    """
    AI Trip Planning Agent.

    Generates day-by-day itineraries considering:
    - Acclimatization requirements (altitude gain limits)
    - Terrain difficulty progression
    - Rest days for high altitude
    - Safety margins
    - Weather seasonality

    Uses actual trek data, never hallucinates routes.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    trek_id = data.get("trek_id")
    if not trek_id:
        return jsonify({"error": "trek_id is required"}), 400

    try:
        planner = TripPlannerAgent()

        preferences = {
            "include_rest_days": data.get("include_rest_days", True),
            "acclimatization_strict": data.get("acclimatization_strict", True),
            "pace": data.get("pace", "moderate"),  # slow, moderate, fast
        }

        result = planner.generate_itinerary(
            trek_id=trek_id,
            user_preferences=preferences,
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Trip planner error: {e}", exc_info=True)
        return jsonify({
            "error": "Trip planning service error",
            "detail": str(e)
        }), 500


# ============================================================================
# PACKING LIST ASSISTANT - Contextual Gear Recommendations
# ============================================================================

@ai_api.route("/packing-list", methods=["POST"])
@jwt_required()
def generate_packing_list():
    """
    AI Packing Assistant generating contextual gear lists based on:
    - Trek altitude & temperature
    - Season & weather patterns
    - Duration
    - Terrain type
    - User experience level

    Categories: Clothing, Equipment, Personal Items, Emergency, Documents
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    trek_id = data.get("trek_id")
    if not trek_id:
        return jsonify({"error": "trek_id is required"}), 400

    try:
        assistant = PackingAssistant()

        trek = Trek.query.get(trek_id)
        if not trek:
            return jsonify({"error": "Trek not found"}), 404

        result = assistant.generate_packing_list(
            trek_id=trek_id,
            altitude_m=trek.max_altitude_m,
            season=data.get("season", "Autumn"),
            duration_days=trek.duration,
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Packing list error: {e}", exc_info=True)
        return jsonify({
            "error": "Packing list service error",
            "detail": str(e)
        }), 500


# ============================================================================
# FITNESS READINESS ASSESSMENT
# ============================================================================

@ai_api.route("/fitness-assessment", methods=["POST"])
@jwt_required()
def assess_fitness():
    """
    Trek fitness readiness assessment with training recommendations.

    Educational tool that analyzes:
    - Current fitness level vs trek requirements
    - Altitude experience gap
    - Cardiovascular preparedness
    - Training timeline needed

    Returns: readiness score, gap analysis, 6-week training program

    DISCLAIMER: Not medical advice. Consult healthcare professionals.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    trek_id = data.get("trek_id")
    if not trek_id:
        return jsonify({"error": "trek_id is required"}), 400

    user = User.query.get(user_id)

    try:
        assessor = ReadinessAssessor()

        fitness_data = {
            "fitness_level": data.get("fitness_level") or user.fitness_level,
            "weekly_cardio_hours": data.get("weekly_cardio_hours", 3.0),
            "max_elevation_experience_m": data.get("max_elevation_experience_m") or user.max_altitude_climbed,
            "recent_training_weeks": data.get("recent_training_weeks", 0),
        }

        result = assessor.assess_readiness(
            trek_id=trek_id,
            user_fitness_data=fitness_data,
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Fitness assessment error: {e}", exc_info=True)
        return jsonify({
            "error": "Fitness assessment service error",
            "detail": str(e)
        }), 500


# ============================================================================
# REVIEW ANALYZER - NLP Sentiment & Aspect Extraction
# ============================================================================

@ai_api.route("/reviews/analyze", methods=["POST"])
@jwt_required()
def analyze_reviews():
    """
    AI Review Analysis using NLP/LLM:
    - Sentiment analysis (positive/negative/neutral)
    - Aspect-based sentiment (guide, safety, route, logistics, weather)
    - Key strengths extraction
    - Concern/complaint extraction
    - Topic clustering

    Helps organizers understand trek feedback at scale.
    """
    data = request.get_json() or {}

    trek_id = data.get("trek_id")
    if not trek_id:
        return jsonify({"error": "trek_id is required"}), 400

    try:
        analyzer = ReviewAnalyzerAgent()

        result = analyzer.analyze_trek_reviews(trek_id=trek_id)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Review analysis error: {e}", exc_info=True)
        return jsonify({
            "error": "Review analysis service error",
            "detail": str(e)
        }), 500


# ============================================================================
# DOCUMENT UPLOAD & INDEXING - RAG Pipeline Entry Point
# ============================================================================

@ai_api.route("/documents/upload", methods=["POST"])
@jwt_required()
def upload_document():
    """
    Upload trek documents for RAG indexing.

    Pipeline:
    1. File upload (PDF, DOCX, TXT, MD)
    2. Text extraction (pypdf, python-docx)
    3. LangChain RecursiveCharacterTextSplitter chunking
    4. Metadata enrichment (trek_id, category, page numbers)
    5. Embedding generation (sentence-transformers/OpenAI)
    6. FAISS vector index insertion
    7. Database persistence

    Organizers can upload: route guides, safety manuals, permits, packing lists
    """
    claims = get_jwt()
    role = claims.get("role")

    if role not in ["admin", "organizer", "staff"]:
        return jsonify({"error": "Only organizers and admins can upload documents"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    trek_id = request.form.get("trek_id", type=int)
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "route_guide")

    if not title:
        title = file.filename

    allowed_extensions = {"pdf", "docx", "doc", "txt", "md"}
    file_ext = file.filename.rsplit(".", 1)[-1].lower()

    if file_ext not in allowed_extensions:
        return jsonify({
            "error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        }), 400

    try:
        import os
        os.makedirs(Config.DOCUMENTS_FOLDER, exist_ok=True)

        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(Config.DOCUMENTS_FOLDER, safe_filename)

        file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Create document record
        doc = TrekDocument(
            trek_id=trek_id,
            organizer_id=int(get_jwt_identity()),
            title=title,
            filename=filename,
            file_path=file_path,
            file_type=file_ext,
            category=category,
            file_size_bytes=file_size,
            is_indexed=False,
            chunk_count=0,
        )
        db.session.add(doc)
        db.session.commit()

        # Index document asynchronously (or synchronously for demo)
        rag_service = get_rag_service()
        chunks_indexed = rag_service.chunk_and_index_document(doc.id)

        logger.info(f"Document uploaded and indexed: {title} ({chunks_indexed} chunks)")

        return jsonify({
            "message": "Document uploaded and indexed successfully",
            "document": doc.to_dict(),
            "chunks_indexed": chunks_indexed,
        }), 201

    except Exception as e:
        logger.error(f"Document upload error: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            "error": "Document upload failed",
            "detail": str(e)
        }), 500


# ============================================================================
# LIST DOCUMENTS
# ============================================================================

@ai_api.route("/documents", methods=["GET"])
@jwt_required()
def list_documents():
    """List trek documents with indexing status."""
    trek_id = request.args.get("trek_id", type=int)
    category = request.args.get("category")

    query = TrekDocument.query

    if trek_id:
        query = query.filter_by(trek_id=trek_id)
    if category:
        query = query.filter_by(category=category)

    documents = query.order_by(TrekDocument.uploaded_at.desc()).all()

    return jsonify({
        "documents": [doc.to_dict() for doc in documents],
        "total": len(documents),
    }), 200


# ============================================================================
# ML DEMAND PREDICTION - Traditional Machine Learning
# ============================================================================

@ai_api.route("/ml/demand-prediction", methods=["POST"])
@jwt_required()
def predict_demand():
    """
    Trek demand prediction using traditional ML (scikit-learn, XGBoost).

    Features:
    - Month, season
    - Trek difficulty, duration, altitude
    - Price range
    - Historical booking patterns
    - Location popularity

    Models: Random Forest, XGBoost
    Returns: Predicted booking volume, demand category (Low/Medium/High)

    Demonstrates traditional ML vs LLM-based AI.
    """
    claims = get_jwt()
    role = claims.get("role")

    if role not in ["admin", "organizer", "staff"]:
        return jsonify({"error": "Only organizers and admins can access demand predictions"}), 403

    data = request.get_json() or {}
    trek_id = data.get("trek_id")

    if not trek_id:
        return jsonify({"error": "trek_id is required"}), 400

    try:
        predictor = DemandPredictor()

        result = predictor.predict_trek_demand(trek_id=trek_id)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Demand prediction error: {e}", exc_info=True)
        return jsonify({
            "error": "Demand prediction service error",
            "detail": str(e)
        }), 500


# ============================================================================
# CONVERSATION HISTORY
# ============================================================================

@ai_api.route("/conversations", methods=["GET"])
@jwt_required()
def get_conversations():
    """List user's AI conversation sessions."""
    user_id = int(get_jwt_identity())

    conversations = Conversation.query.filter_by(user_id=user_id).order_by(
        Conversation.updated_at.desc()
    ).limit(20).all()

    return jsonify({
        "conversations": [conv.to_dict() for conv in conversations],
        "total": len(conversations),
    }), 200


@ai_api.route("/conversations/<session_id>", methods=["GET"])
@jwt_required()
def get_conversation_messages(session_id):
    """Get messages from a specific conversation."""
    user_id = int(get_jwt_identity())

    conv = Conversation.query.filter_by(session_id=session_id, user_id=user_id).first()
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    return jsonify(conv.to_dict(include_messages=True)), 200


# ============================================================================
# ADMIN AI ANALYTICS - Observability Dashboard
# ============================================================================

@ai_api.route("/admin/analytics", methods=["GET"])
@jwt_required()
def ai_analytics():
    """
    AI usage analytics for admin dashboard.

    Metrics:
    - Total AI requests by type
    - Average response latency
    - Model usage distribution
    - RAG retrieval statistics
    - Grounding scores
    - Error rates
    - Token consumption
    - Tool usage frequency
    """
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    try:
        from sqlalchemy import func

        # Total interactions by type
        interaction_counts = db.session.query(
            AIInteractionLog.request_type,
            func.count(AIInteractionLog.id).label("count")
        ).group_by(AIInteractionLog.request_type).all()

        # Average latency per request type
        avg_latencies = db.session.query(
            AIInteractionLog.request_type,
            func.avg(AIInteractionLog.latency_ms).label("avg_latency")
        ).group_by(AIInteractionLog.request_type).all()

        # Model usage
        model_usage = db.session.query(
            AIInteractionLog.model_used,
            func.count(AIInteractionLog.id).label("count")
        ).group_by(AIInteractionLog.model_used).all()

        # Token consumption
        total_tokens = db.session.query(
            func.sum(AIInteractionLog.prompt_tokens).label("prompt_tokens"),
            func.sum(AIInteractionLog.completion_tokens).label("completion_tokens")
        ).first()

        # Grounding scores
        avg_grounding = db.session.query(
            func.avg(AIInteractionLog.grounding_score).label("avg_grounding")
        ).first()

        # Error rate
        total_requests = AIInteractionLog.query.count()
        error_requests = AIInteractionLog.query.filter(AIInteractionLog.was_safe == False).count()

        # Recent logs
        recent_logs = AIInteractionLog.query.order_by(
            AIInteractionLog.timestamp.desc()
        ).limit(50).all()

        return jsonify({
            "total_requests": total_requests,
            "error_rate": round(error_requests / total_requests * 100, 2) if total_requests > 0 else 0,
            "interaction_counts": [
                {"type": t, "count": c} for t, c in interaction_counts
            ],
            "avg_latencies": [
                {"type": t, "latency_ms": round(l, 0)} for t, l in avg_latencies
            ],
            "model_usage": [
                {"model": m, "count": c} for m, c in model_usage
            ],
            "token_consumption": {
                "prompt_tokens": total_tokens.prompt_tokens or 0,
                "completion_tokens": total_tokens.completion_tokens or 0,
                "total_tokens": (total_tokens.prompt_tokens or 0) + (total_tokens.completion_tokens or 0),
            },
            "avg_grounding_score": round(avg_grounding.avg_grounding or 1.0, 3),
            "recent_logs": [log.to_dict() for log in recent_logs],
        }), 200

    except Exception as e:
        logger.error(f"Analytics error: {e}", exc_info=True)
        return jsonify({
            "error": "Analytics service error",
            "detail": str(e)
        }), 500


# ============================================================================
# SEMANTIC SEARCH - Vector Similarity Search
# ============================================================================

@ai_api.route("/search/semantic", methods=["POST"])
@jwt_required()
def semantic_search():
    """
    Semantic trek search using embeddings and vector similarity.

    Example queries:
    - "peaceful forest trek with mountain views"
    - "challenging high altitude expedition"
    - "beginner friendly trek near lakes"

    Uses cosine similarity in vector space.
    """
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "query is required"}), 400

    try:
        vector_store = get_vector_store()
        embedding_service = get_embedding_service()

        # Generate query embedding
        query_embedding = embedding_service.embed_text(query)

        # Search vector store
        results = vector_store.similarity_search(
            query=query,
            k=data.get("top_k", 5),
            score_threshold=0.3,
        )

        # Group by trek_id to avoid duplicates
        trek_ids = list(set([r.get("trek_id") for r in results if r.get("trek_id")]))
        treks = Trek.query.filter(Trek.id.in_(trek_ids)).all()

        return jsonify({
            "query": query,
            "results": [t.to_dict() for t in treks],
            "total": len(treks),
        }), 200

    except Exception as e:
        logger.error(f"Semantic search error: {e}", exc_info=True)
        return jsonify({
            "error": "Semantic search service error",
            "detail": str(e)
        }), 500
