from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(25))
    role = db.Column(db.String(20), nullable=False, default="trekker")  # trekker (user) | organizer (staff) | admin
    status = db.Column(db.String(20), nullable=False, default="active")  # active | inactive | blacklisted

    # Trekker Profile & Medical/Fitness
    experience_level = db.Column(db.String(30), default="Beginner")  # beginner | intermediate | advanced | expert
    fitness_level = db.Column(db.String(30), default="Moderate")     # low | moderate | high | athletic
    preferred_difficulty = db.Column(db.String(20), default="Moderate")
    max_altitude_climbed = db.Column(db.Integer, default=2500)       # meters
    budget_preference = db.Column(db.Float, default=15000.0)
    max_budget = db.Column(db.Float, default=15000.0)
    medical_conditions = db.Column(db.Text, nullable=True)
    medical_info = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(150), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", backref="user", lazy=True, cascade="all, delete-orphan")
    guide_profile = db.relationship("GuideProfile", backref="user", uselist=False, cascade="all, delete-orphan", foreign_keys="GuideProfile.user_id")
    reviews = db.relationship("Review", backref="user", lazy=True, cascade="all, delete-orphan")
    conversations = db.relationship("Conversation", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_normalized_role(self):
        # Normalize legacy roles: 'user' -> 'trekker', 'staff' -> 'organizer'
        if self.role in ["user", "trekker"]:
            return "trekker"
        if self.role in ["staff", "organizer"]:
            return "organizer"
        return "admin"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.get_normalized_role(),
            "raw_role": self.role,
            "status": self.status,
            "experience_level": self.experience_level or "Beginner",
            "fitness_level": self.fitness_level or "Moderate",
            "preferred_difficulty": self.preferred_difficulty or "Moderate",
            "max_altitude_climbed": self.max_altitude_climbed or 2500,
            "budget_preference": self.budget_preference or self.max_budget or 15000.0,
            "max_budget": self.max_budget or self.budget_preference or 15000.0,
            "medical_conditions": self.medical_conditions or self.medical_info,
            "medical_info": self.medical_info or self.medical_conditions,
            "emergency_contact": self.emergency_contact,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GuideProfile(db.Model):
    __tablename__ = "staff_profiles"  # Retain table name for schema compatibility

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, unique=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(25), nullable=True)
    contact_number = db.Column(db.String(25), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    specialization = db.Column(db.String(150), default="High Altitude Guide")
    experience_years = db.Column(db.Integer, default=3)
    certifications = db.Column(db.String(255), default="NIM Basic & Advanced Mountaineering, Wilderness First Aid")
    spoken_languages = db.Column(db.String(150), default="English, Hindi")
    rating = db.Column(db.Float, default=4.8)
    status = db.Column(db.String(20), nullable=False, default="active")  # active | inactive
    is_active = db.Column(db.Boolean, default=True)
    emergency_contact = db.Column(db.String(150), nullable=True)

    assigned_treks = db.relationship("Trek", backref="assigned_guide", lazy=True, foreign_keys="Trek.assigned_staff_id")

    def to_dict(self):
        guide_name = self.name or (self.user.name if self.user else "Mountain Guide")
        guide_email = self.email or (self.user.email if self.user else "")
        guide_phone = self.phone or self.contact_number or (self.user.phone if self.user else "")

        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": guide_name,
            "email": guide_email,
            "phone": guide_phone,
            "contact_number": guide_phone,
            "bio": self.bio,
            "specialization": self.specialization,
            "experience_years": self.experience_years,
            "certifications": self.certifications,
            "spoken_languages": self.spoken_languages,
            "rating": round(self.rating or 4.8, 2),
            "status": self.status,
            "is_active": self.is_active if self.is_active is not None else (self.status == "active"),
            "emergency_contact": self.emergency_contact,
            "assigned_treks_count": len(self.assigned_treks) if self.assigned_treks else 0,
        }


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(150), nullable=False, index=True)
    slug = db.Column(db.String(150), unique=True, index=True)
    location = db.Column(db.String(150), nullable=False)
    region = db.Column(db.String(100), default="Himalayas")
    country = db.Column(db.String(50), default="India")
    difficulty = db.Column(db.String(30), nullable=False, default="Moderate")  # Easy | Moderate | Difficult | Expert
    duration = db.Column(db.Integer, nullable=False, default=5)               # In days
    distance_km = db.Column(db.Float, default=35.0)                           # Total trail km
    max_altitude_m = db.Column(db.Integer, default=3800)                      # Peak meters
    base_camp = db.Column(db.String(100), default="Base Camp")
    best_season = db.Column(db.String(100), default="May - June, Sep - Oct") # Seasons
    price = db.Column(db.Float, nullable=False, default=9500.0)               # Per person
    available_slots = db.Column(db.Integer, nullable=False, default=15)
    total_slots = db.Column(db.Integer, nullable=False, default=20)

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staff_profiles.id"), nullable=True)
    guide_id = db.Column(db.Integer, db.ForeignKey("staff_profiles.id"), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    status = db.Column(db.String(20), nullable=False, default="Open")          # Open | Closed | Pending | Completed
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    highlights = db.Column(db.Text)                                           # JSON or comma-separated
    safety_guidelines = db.Column(db.Text)
    gear_requirements = db.Column(db.Text)
    permits_required = db.Column(db.String(255), default="Forest Department Permit")
    image = db.Column(db.String(350))

    coordinates_lat = db.Column(db.Float, nullable=True)
    coordinates_lng = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    rating_avg = db.Column(db.Float, default=4.8)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", backref="trek", lazy=True, cascade="all, delete-orphan")
    itinerary_items = db.relationship("ItineraryItem", backref="trek", lazy=True, cascade="all, delete-orphan", order_by="ItineraryItem.day_number")
    documents = db.relationship("TrekDocument", backref="trek", lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="trek", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_itinerary=False, include_guide=False):
        lat = self.latitude if self.latitude is not None else self.coordinates_lat
        lng = self.longitude if self.longitude is not None else self.coordinates_lng

        data = {
            "id": self.id,
            "trek_name": self.trek_name,
            "slug": self.slug or f"trek-{self.id}",
            "location": self.location,
            "region": self.region,
            "country": self.country,
            "difficulty": self.difficulty,
            "duration": self.duration,
            "distance_km": self.distance_km,
            "max_altitude_m": self.max_altitude_m,
            "base_camp": self.base_camp,
            "best_season": self.best_season,
            "price": self.price,
            "available_slots": self.available_slots,
            "total_slots": self.total_slots,
            "assigned_staff_id": self.assigned_staff_id or self.guide_id,
            "guide_id": self.guide_id or self.assigned_staff_id,
            "organizer_id": self.organizer_id,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "description": self.description,
            "highlights": self.highlights,
            "safety_guidelines": self.safety_guidelines,
            "gear_requirements": self.gear_requirements,
            "permits_required": self.permits_required,
            "image": self.image,
            "latitude": lat,
            "longitude": lng,
            "coordinates": {
                "lat": lat,
                "lng": lng
            } if lat is not None else None,
            "rating_avg": round(self.rating_avg or 4.5, 1),
            "review_count": self.review_count or 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_guide and self.assigned_guide:
            data["assigned_guide"] = self.assigned_guide.to_dict()
        if include_itinerary:
            data["itinerary"] = [item.to_dict() for item in self.itinerary_items]
        return data


class ItineraryItem(db.Model):
    __tablename__ = "itinerary_items"

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    altitude_m = db.Column(db.Integer, nullable=True)
    start_altitude_m = db.Column(db.Integer, nullable=True)
    end_altitude_m = db.Column(db.Integer, nullable=True)
    distance_km = db.Column(db.Float, default=0.0)
    trekking_time_hours = db.Column(db.Float, default=5.0)

    campsite = db.Column(db.String(100), default="Alpine Campsite")
    overnight_stay = db.Column(db.String(100), default="Tents / Alpine Campsite")
    meals_included = db.Column(db.String(100), default="Breakfast, Lunch, Dinner")
    acclimatization_notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        alt = self.altitude_m or self.end_altitude_m or self.start_altitude_m
        camp = self.campsite or self.overnight_stay
        return {
            "id": self.id,
            "trek_id": self.trek_id,
            "day_number": self.day_number,
            "title": self.title,
            "description": self.description,
            "altitude_m": alt,
            "start_altitude_m": self.start_altitude_m or alt,
            "end_altitude_m": self.end_altitude_m or alt,
            "distance_km": self.distance_km,
            "trekking_time_hours": self.trekking_time_hours,
            "campsite": camp,
            "overnight_stay": camp,
            "meals_included": self.meals_included,
            "acclimatization_notes": self.acclimatization_notes,
        }


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(50), nullable=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), nullable=False, default="Booked")  # Booked | PendingConfirmation | Cancelled | Completed | confirmed | pending
    amount = db.Column(db.Float, nullable=False, default=0.0)
    total_price = db.Column(db.Float, nullable=True)
    participants_count = db.Column(db.Integer, default=1)
    num_participants = db.Column(db.Integer, default=1)
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(25), nullable=True)
    special_requests = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(20), default="Card")  # Card | UPI | Cash | NetBanking
    payment_status = db.Column(db.String(20), nullable=False, default="Paid")  # Paid | Pending | Refunded | paid | pending
    completed_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        amt = self.amount if self.amount else (self.total_price or 0.0)
        p_count = self.participants_count or self.num_participants or 1

        return {
            "id": self.id,
            "booking_code": self.booking_code or f"TMA-{self.id}",
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "user_phone": self.user.phone if self.user else None,
            "trek_id": self.trek_id,
            "trek_name": self.trek.trek_name if self.trek else None,
            "location": self.trek.location if self.trek else None,
            "difficulty": self.trek.difficulty if self.trek else None,
            "duration": self.trek.duration if self.trek else None,
            "max_altitude_m": self.trek.max_altitude_m if self.trek else None,
            "start_date": self.trek.start_date.isoformat() if self.trek and self.trek.start_date else None,
            "end_date": self.trek.end_date.isoformat() if self.trek and self.trek.end_date else None,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "status": self.status,
            "amount": amt,
            "total_price": amt,
            "participants_count": p_count,
            "num_participants": p_count,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "special_requests": self.special_requests,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
        }


class TrekDocument(db.Model):
    __tablename__ = "trek_documents"

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=True)  # Can be trek-specific or general
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, default=1)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(255), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(350), nullable=False)
    file_type = db.Column(db.String(20), default="pdf")  # pdf | docx | txt | md
    category = db.Column(db.String(50), default="route_guide")
    file_size_bytes = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer, default=0)
    chunk_count = db.Column(db.Integer, default=0)
    is_indexed = db.Column(db.Boolean, default=False)
    summary = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    chunks = db.relationship("DocumentChunk", backref="document", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        fname = self.filename or self.file_name or "document.txt"
        fsize = self.file_size_bytes or self.file_size or 0
        return {
            "id": self.id,
            "trek_id": self.trek_id,
            "trek_name": self.trek.trek_name if self.trek else "General Trekking Guide",
            "organizer_id": self.organizer_id,
            "title": self.title,
            "filename": fname,
            "file_name": fname,
            "file_type": self.file_type,
            "category": self.category,
            "file_size_bytes": fsize,
            "file_size": fsize,
            "chunk_count": self.chunk_count,
            "is_indexed": self.is_indexed,
            "summary": self.summary,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }


class DocumentChunk(db.Model):
    __tablename__ = "document_chunks"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("trek_documents.id"), nullable=False)
    trek_id = db.Column(db.Integer, nullable=True, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, default=1)
    section_header = db.Column(db.String(150), default="General Information")
    token_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "trek_id": self.trek_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "page_number": self.page_number,
            "section_header": self.section_header,
            "token_count": self.token_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)  # 1-5
    comment = db.Column(db.Text, nullable=False)
    difficulty_felt = db.Column(db.String(20), default="As Described")  # Easier | As Described | Harder
    weather_encountered = db.Column(db.String(50), default="Clear & Sunny")
    guide_rating = db.Column(db.Float, default=5.0)

    # NLP / Sentiment Analysis Outputs
    sentiment_score = db.Column(db.Float, default=0.8)       # -1.0 to +1.0
    sentiment_label = db.Column(db.String(20), default="Positive")  # Positive | Neutral | Negative
    aspect_scores = db.Column(db.JSON, nullable=True)        # JSON: {safety, guide, route, food, logistics}
    aspect_ratings = db.Column(db.JSON, nullable=True)       # JSON: alias for aspect_scores
    key_positives = db.Column(db.JSON, nullable=True)        # JSON: list of extracted positives
    key_concerns = db.Column(db.JSON, nullable=True)         # JSON: list of extracted concerns

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        aspects = self.aspect_ratings or self.aspect_scores or {}
        positives = self.key_positives or []
        concerns = self.key_concerns or []

        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "Anonymous Trekker",
            "trek_id": self.trek_id,
            "trek_name": self.trek.trek_name if self.trek else None,
            "rating": self.rating,
            "comment": self.comment,
            "difficulty_felt": self.difficulty_felt,
            "weather_encountered": self.weather_encountered,
            "guide_rating": self.guide_rating,
            "sentiment_score": round(self.sentiment_score or 0.0, 2),
            "sentiment_label": self.sentiment_label or "Positive",
            "aspect_scores": aspects,
            "aspect_ratings": aspects,
            "key_positives": positives,
            "key_concerns": concerns,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_id = db.Column(db.String(100), unique=True, index=True)
    title = db.Column(db.String(150), default="Trekking Consultation")
    selected_trek_id = db.Column(db.Integer, nullable=True)
    context_data = db.Column(db.Text, nullable=True)  # JSON for state / memory
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship("Message", backref="conversation", lazy=True, cascade="all, delete-orphan", order_by="Message.id")

    def to_dict(self, include_messages=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "title": self.title,
            "selected_trek_id": self.selected_trek_id,
            "message_count": len(self.messages) if self.messages else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_messages:
            data["messages"] = [m.to_dict() for m in self.messages]
        return data


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user | assistant | system | tool
    content = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(50), nullable=True) # recommendation | rag | planning | booking | fitness | general
    sources = db.Column(db.Text, nullable=True)      # JSON list of source citations
    tool_calls = db.Column(db.Text, nullable=True)   # JSON list of tool executions
    latency_ms = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        sources_list = []
        tools_list = []
        try:
            if self.sources:
                sources_list = json.loads(self.sources) if isinstance(self.sources, str) else self.sources
            if self.tool_calls:
                tools_list = json.loads(self.tool_calls) if isinstance(self.tool_calls, str) else self.tool_calls
        except Exception:
            pass

        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "intent": self.intent,
            "sources": sources_list,
            "tool_calls": tools_list,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AIInteractionLog(db.Model):
    __tablename__ = "ai_interaction_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=True)
    request_type = db.Column(db.String(50), nullable=False) # chat | rag | recommendation | trip_plan | packing | readiness | demand_pred
    model_used = db.Column(db.String(60), default="mock-rules-engine")
    prompt_tokens = db.Column(db.Integer, default=0)
    completion_tokens = db.Column(db.Integer, default=0)
    latency_ms = db.Column(db.Integer, default=0)
    tool_used = db.Column(db.String(80), nullable=True)
    retrieval_count = db.Column(db.Integer, default=0)
    grounding_score = db.Column(db.Float, default=1.0) # 0.0 to 1.0
    was_safe = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request_type": self.request_type,
            "model_used": self.model_used,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "latency_ms": self.latency_ms,
            "tool_used": self.tool_used,
            "retrieval_count": self.retrieval_count,
            "grounding_score": round(self.grounding_score or 1.0, 2),
            "was_safe": self.was_safe,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class TrekRecommendationLog(db.Model):
    __tablename__ = "trek_recommendation_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    preferences = db.Column(db.Text, nullable=False)      # JSON of user input
    recommended_trek_ids = db.Column(db.Text, nullable=False) # JSON list
    scores = db.Column(db.Text, nullable=True)           # JSON dict of trek_id -> match_score
    match_reasons = db.Column(db.Text, nullable=True)    # JSON dict of trek_id -> list of reasons
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        prefs = {}
        trek_ids = []
        score_map = {}
        reasons_map = {}
        try:
            if self.preferences:
                prefs = json.loads(self.preferences) if isinstance(self.preferences, str) else self.preferences
            if self.recommended_trek_ids:
                trek_ids = json.loads(self.recommended_trek_ids) if isinstance(self.recommended_trek_ids, str) else self.recommended_trek_ids
            if self.scores:
                score_map = json.loads(self.scores) if isinstance(self.scores, str) else self.scores
            if self.match_reasons:
                reasons_map = json.loads(self.match_reasons) if isinstance(self.match_reasons, str) else self.match_reasons
        except Exception:
            pass

        return {
            "id": self.id,
            "user_id": self.user_id,
            "preferences": prefs,
            "recommended_trek_ids": trek_ids,
            "scores": score_map,
            "match_reasons": reasons_map,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Aliases for compatibility
StaffProfile = GuideProfile
Guide = GuideProfile
Itinerary = ItineraryItem
