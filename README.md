# TrekMate AI – Intelligent Trekking Management & Adventure Assistant

A production-grade full-stack application demonstrating practical AI Engineering skills through a complete trekking management platform powered by **Generative AI, RAG, LangChain, LangGraph, Vector Databases, Traditional ML, and intelligent agent orchestration**.

🚀 **Live Demo**: [trekking-management-sand.vercel.app](https://trekking-management-sand.vercel.app)  
📂 **GitHub**: [sweta1233/Trekking-management-app](https://github.com/sweta1233/Trekking-management-app)

---

## 🎯 Project Overview

TrekMate AI is not just another chatbot-enabled application. It's a comprehensive AI-powered platform that demonstrates:

- **RAG (Retrieval-Augmented Generation)** with document chunking, vector search, and grounded responses
- **LangGraph** multi-agent orchestration with intelligent intent routing
- **LangChain** for document processing, embeddings, and retrieval pipelines
- **Vector databases** (FAISS) for semantic search and similarity matching
- **Traditional ML** (scikit-learn, XGBoost) for demand prediction
- **NLP & Sentiment Analysis** for review analytics
- **Embeddings** for personalized recommendations
- **Multi-agent workflows** with tool calling and state management

---

## 🏗️ Architecture

```
Frontend (Vue.js)
        ↓
   REST API (Flask)
        ↓
   AI Orchestrator
        ↓
     LangGraph
        ↓
   ┌────────┴─────────┐
   ↓                  ↓
RAG Agent      Recommendation Engine
   ↓                  ↓
LangChain        Embeddings
   ↓                  ↓
Vector DB        ML Models
(FAISS)         (scikit-learn)
```

---

## 🚀 Key Features

### **For Trekkers (Users)**
- 🤖 **AI Assistant** powered by LangGraph with intelligent routing
- 🎯 **Personalized Recommendations** using embeddings & semantic matching
- 📚 **RAG-based Q&A** - Ask questions, get answers with source citations
- 🗓️ **AI Trip Planner** - Generate day-by-day itineraries with acclimatization
- 🎒 **Smart Packing Lists** - Contextual gear recommendations
- 💪 **Fitness Assessment** - Trek readiness evaluation with training plans
- 🔍 **Semantic Search** - Find treks using natural language

### **For Trek Organizers**
- 📄 **Document Upload** for RAG indexing (PDFs, DOCX, TXT, MD)
- 📊 **Review Analytics** - NLP sentiment analysis & aspect extraction
- 📈 **Demand Prediction** - Traditional ML forecasting
- 🧑‍🤝‍🧑 **Guide Management**
- 📅 **Trek & Itinerary Management**

### **For Admins**
- 📊 **AI Analytics Dashboard** - Usage metrics, latency, token consumption
- 👥 **User & Staff Management**
- 💰 **Revenue Reports**
- 🔍 **Advanced Search**

---

## 🛠️ Technology Stack

### **Frontend**
- **Vue.js 3** - Progressive framework
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **Vue Router** - Navigation

### **Backend**
- **Python 3.10+**
- **Flask** - REST API framework
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **Flask-Caching** - Redis/SimpleCache

### **AI/ML Stack**
| Technology | Purpose |
|-----------|---------|
| **LangChain** | Document loading, text splitting, embeddings, retrievers |
| **LangGraph** | Multi-agent orchestration, stateful workflows |
| **FAISS** | Vector database for similarity search |
| **OpenAI / Anthropic / Gemini** | LLM providers (configurable) |
| **sentence-transformers** | Local embeddings (HuggingFace) |
| **pypdf / python-docx** | Document parsing |
| **scikit-learn** | Traditional ML models |
| **XGBoost** | Gradient boosting |
| **pandas / NumPy** | Data manipulation |

### **Database**
- **PostgreSQL** (production)
- **SQLite** (development)

---

## 📊 Database Schema

```
users
├── id, name, email, password_hash, role, status
├── experience_level, fitness_level, preferred_difficulty
├── max_altitude_climbed, budget_preference
└── medical_conditions, emergency_contact

treks
├── id, trek_name, location, region, difficulty
├── duration, distance_km, max_altitude_m
├── price, available_slots, start_date, end_date
└── description, safety_guidelines, gear_requirements

trek_documents (RAG Pipeline)
├── id, trek_id, title, file_path, file_type, category
├── chunk_count, is_indexed, summary
└── chunks → document_chunks

document_chunks
├── id, document_id, trek_id, chunk_index
├── content, page_number, section_header
└── (embedded in FAISS vector store)

reviews (NLP/Sentiment Analysis)
├── id, user_id, trek_id, rating, comment
├── sentiment_score, sentiment_label
├── aspect_scores (JSON: safety, guide, route, food)
└── key_positives, key_concerns (JSON)

conversations (AI Chat History)
├── id, user_id, session_id, title
└── messages → messages table

ai_interaction_logs (Observability)
├── id, user_id, session_id, request_type
├── model_used, prompt_tokens, completion_tokens
├── latency_ms, tool_used, retrieval_count
└── grounding_score, was_safe

trek_recommendation_logs
├── id, user_id, preferences (JSON)
├── recommended_trek_ids (JSON)
└── scores, match_reasons (JSON)
```

---

## 🤖 AI Agent Architecture (LangGraph)

### **Intent Classification → Dynamic Routing**

```
User Query
    ↓
Intent Classifier (rule-based + keyword)
    ↓
Router
    ├── Recommendation Agent → Embeddings + Semantic Matching
    ├── RAG Information Agent → Vector Search + Document Retrieval
    ├── Trip Planning Agent → Itinerary Generation
    ├── Booking Agent → Database Tools
    ├── Fitness/Readiness Agent → Assessment Logic
    ├── Packing Assistant → Contextual Gear Lists
    ├── Review Analytics Agent → NLP Sentiment
    └── General Assistant → Direct LLM
    ↓
Response Generator (Markdown formatting)
    ↓
Safety/Grounding Validator
    ↓
Structured Response + Sources + Metadata
```

### **Example Query Flow**

**User**: *"Which trek is best for beginners in winter?"*

1. **Intent Classifier** → `recommendation`
2. **Recommendation Agent**:
   - Extracts user profile (experience: beginner)
   - Filters treks (difficulty: Easy, season: winter)
   - Computes embeddings similarity
   - Ranks by match score
3. **Response Generator**:
   - Formats top 3 recommendations
   - Adds match reasons
4. **Safety Validator**:
   - Checks for altitude safety notes
5. **Returns**: Structured response with trek cards, match explanations

---

## 📚 RAG Pipeline (Retrieval-Augmented Generation)

### **Document Ingestion Flow**

```
PDF/DOCX Upload
    ↓
Text Extraction (pypdf, python-docx)
    ↓
LangChain RecursiveCharacterTextSplitter
    • chunk_size: 600 tokens
    • chunk_overlap: 120 tokens
    ↓
Metadata Enrichment
    • trek_id, document_id, page_number
    • section_header (detected from text)
    • category (route_guide, safety, permits)
    ↓
Embedding Generation
    • OpenAI text-embedding-3-small, or
    • HuggingFace sentence-transformers
    ↓
FAISS Vector Index
    • Stored in backend/instances/faiss_index/
    • Cosine similarity search
    ↓
Database Persistence (document_chunks table)
```

### **Query Flow**

```
User Query: "How to prevent altitude sickness?"
    ↓
Query Embedding
    ↓
FAISS Similarity Search (top_k=4, threshold=0.05)
    ↓
Retrieved Chunks with Metadata
    • Document title, page number, section
    • Similarity score
    ↓
Context Assembly
    • Format with citations
    • Include trek database info if trek_id provided
    ↓
LLM Synthesis (with grounding rules)
    • System prompt enforces source citation
    • Temperature: 0.3 for factual accuracy
    ↓
Grounded Answer + Source Citations
    • Grounding score computed (word overlap)
    • Page numbers & document references
```

---

## 🎯 Trek Recommendation Engine

### **Hybrid Scoring System**

```python
User Profile:
  - experience_level: "Beginner"
  - fitness_level: "Moderate"
  - budget: ₹12,000
  - max_altitude: 2,500m
  - preferred_difficulty: "Easy"
  - interests: "snow, lakes, forests"

↓

Candidate Filtering:
  - difficulty ≤ user.preferred_difficulty
  - price ≤ user.budget * 1.2
  - max_altitude ≤ user.max_altitude * 1.5

↓

Semantic Similarity (Embeddings):
  - Embed user interests
  - Embed trek descriptions
  - Cosine similarity score

↓

Rule-Based Scoring:
  - Difficulty match: +30 points
  - Budget match: +25 points
  - Altitude match: +20 points
  - Duration match: +15 points
  - Season match: +10 points

↓

Final Score = (semantic_score * 40) + (rule_score * 60)

↓

Top N Recommendations with Match Reasons
```

---

## 🧪 Traditional ML Component

### **Trek Demand Prediction**

**Purpose**: Demonstrate classical ML alongside LLM-based AI

**Features**:
- Month, season (cyclical encoding)
- Trek difficulty (one-hot)
- Duration, altitude, distance
- Price range
- Location popularity
- Historical booking patterns

**Models Trained**:
- Random Forest Regressor
- XGBoost

**Evaluation Metrics**:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score

**Output**:
- Predicted booking volume
- Demand category: Low / Medium / High
- Confidence interval

---

## 🔐 Safety & Grounding

TrekMate AI implements strict safety measures:

### **RAG Grounding**
- ✅ All factual answers cite source documents
- ✅ Page numbers and sections provided
- ✅ Grounding score computed (0.0–1.0)
- ✅ "Insufficient information" when sources don't cover query

### **High-Altitude Safety**
- ⚠️ Never claims a trek is "safe" solely based on AI
- ⚠️ Always includes acclimatization warnings for >3,000m
- ⚠️ Directs users to medical professionals for health questions
- ⚠️ Emergency protocols in all safety documents

### **No Medical Diagnosis**
- ❌ Fitness assessment is **educational only**
- ❌ Always includes disclaimer to consult doctors
- ❌ Never guarantees physical readiness

### **No Hallucination**
- ✅ Trip planner uses actual trek data from database
- ✅ Clearly states when information is unavailable
- ✅ Never invents route details or safety information

---

## 📦 Installation & Setup

### **Prerequisites**
- Python 3.10+
- Node.js 18+
- Redis (optional, for caching)
- PostgreSQL (for production) or SQLite (for dev)

### **Backend Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# For offline development (no API keys):
# Set LLM_PROVIDER=mock and EMBEDDING_PROVIDER=mock

# For full AI features:
# Set LLM_PROVIDER=openai and add your OPENAI_API_KEY

# Initialize database & seed sample data
python seeds.py

# Run the backend
python app.py
```

Backend runs at **http://localhost:5000**

### **Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoint (if needed)
# Create .env file:
echo "VITE_API_BASE_URL=http://localhost:5000/api" > .env

# Run development server
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## 🔑 Default Credentials

**Admin**:
- Email: `admin@tma.com`
- Password: `Admin@123`

**Sample Users** (created by seeds.py):
- `priya.sharma@example.com` / `Test@123` (Beginner)
- `rajesh.kumar@example.com` / `Test@123` (Intermediate)
- `ananya.reddy@example.com` / `Test@123` (Advanced)

---

## 🚀 API Endpoints

### **AI Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/chat` | POST | LangGraph multi-agent chat |
| `/api/ai/rag/query` | POST | RAG document Q&A |
| `/api/ai/recommend` | POST | Personalized trek recommendations |
| `/api/ai/trip-planner` | POST | AI itinerary generation |
| `/api/ai/packing-list` | POST | Contextual packing lists |
| `/api/ai/fitness-assessment` | POST | Readiness evaluation |
| `/api/ai/reviews/analyze` | POST | NLP sentiment analysis |
| `/api/ai/documents/upload` | POST | Document upload & indexing |
| `/api/ai/documents` | GET | List indexed documents |
| `/api/ai/ml/demand-prediction` | POST | ML demand forecasting |
| `/api/ai/search/semantic` | POST | Vector similarity search |
| `/api/ai/conversations` | GET | Chat history |
| `/api/ai/admin/analytics` | GET | AI usage metrics (admin) |

### **Core Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | JWT authentication |
| `/api/treks` | GET | List treks with filters |
| `/api/treks/:id` | GET | Trek details |
| `/api/treks` | POST | Create trek (admin) |
| `/api/bookings` | POST | Book a trek |
| `/api/bookings` | GET | User's bookings |
| `/api/reviews` | POST | Submit review |
| `/api/dashboard/admin` | GET | Admin dashboard |
| `/api/reports` | GET | Analytics reports |

---

## 🧪 Testing the AI Features

### **1. Test RAG Pipeline**

```bash
# Upload a document
curl -X POST http://localhost:5000/api/ai/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@trek_guide.pdf" \
  -F "title=Kedarkantha Safety Guide" \
  -F "category=safety" \
  -F "trek_id=1"

# Query the RAG system
curl -X POST http://localhost:5000/api/ai/rag/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the symptoms of altitude sickness?",
    "trek_id": 1
  }'
```

### **2. Test AI Chat (LangGraph)**

```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Which trek is best for beginners?",
    "session_id": "test_session_1"
  }'
```

### **3. Test Recommendations**

```bash
curl -X POST http://localhost:5000/api/ai/recommend \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "experience_level": "Beginner",
    "budget": 15000,
    "duration_days": 5,
    "interests": "snow trekking with mountain views"
  }'
```

---

## 📊 Observability & Analytics

### **AI Interaction Logs**

Every AI request is logged with:
- Request type (chat, rag, recommendation, etc.)
- Model used
- Token consumption (prompt + completion)
- Latency (ms)
- Retrieval count (for RAG)
- Grounding score
- Tool calls made
- Success/error status

### **Admin Analytics Dashboard**

Access at `/admin/ai-analytics` (admin only):
- Total AI requests by type
- Average latency per request type
- Model usage distribution
- Token consumption trends
- Grounding score averages
- Error rates
- Tool usage frequency
- Recent interaction logs

---

## 🐳 Docker Deployment

### **Using Docker Compose**

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Services:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:5173
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## 🌍 Environment Variables

See `backend/.env.example` for all configuration options.

### **Key Variables**

```bash
# LLM Provider
LLM_PROVIDER=openai  # or anthropic, gemini, mock
OPENAI_API_KEY=your-key

# Embeddings
EMBEDDING_PROVIDER=openai  # or huggingface, mock
EMBEDDING_MODEL=text-embedding-3-small

# RAG Settings
RAG_CHUNK_SIZE=600
RAG_CHUNK_OVERLAP=120
RAG_TOP_K=4

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/trekmate
```

---

## 📈 Performance Considerations

### **Token Optimization**
- Chunk size: 600 tokens (balance between context and retrieval precision)
- Chunk overlap: 120 tokens (preserve context across boundaries)
- Top-k: 4 chunks (sufficient context without token bloat)
- Temperature: 0.3 for factual queries (reduce hallucination)

### **Caching Strategy**
- Trek listings cached for 5 minutes
- Vector embeddings cached in FAISS index
- User sessions maintained in Redis

### **Cost Estimation** (with OpenAI)
- Average chat query: ~500 input + 300 output tokens
- RAG query: ~1,200 input + 400 output tokens
- Cost per 1,000 queries: ~$2-5 USD

---

## 🎓 Interview Readiness

### **Questions You Can Answer**

1. **Why did you use RAG instead of fine-tuning?**
   - Domain-specific documents change frequently
   - Source attribution required
   - Cost-effective vs fine-tuning
   - Easier to update knowledge base

2. **Explain your LangGraph workflow**
   - Intent classification routes to specialized agents
   - Each agent uses specific tools (RAG, DB, ML)
   - State maintained across agent transitions
   - Response synthesis aggregates results

3. **How does your vector store work?**
   - Documents chunked via RecursiveCharacterTextSplitter
   - Chunks embedded with sentence-transformers
   - FAISS index for cosine similarity search
   - Metadata filtering by trek_id, category

4. **Why use traditional ML alongside LLMs?**
   - Demand prediction is tabular data (not NLP)
   - XGBoost faster and cheaper than LLM
   - Demonstrates understanding of when NOT to use LLMs
   - Hybrid approach shows ML breadth

5. **How do you prevent hallucination?**
   - RAG grounds responses in documents
   - Source citations mandatory
   - Grounding score computed
   - Clear "insufficient information" when knowledge gaps

6. **How does your recommendation system work?**
   - Hybrid: embeddings (semantic) + rules (constraints)
   - User profile embedding × trek description embedding
   - Filters: budget, altitude, difficulty
   - Explainable match reasons

---

## 🔮 Future Enhancements

- [ ] Multi-modal: Image analysis of trek routes
- [ ] Real-time weather integration
- [ ] Voice assistant (Whisper API)
- [ ] Mobile app (React Native)
- [ ] Advanced ML: Neural collaborative filtering
- [ ] Multi-language support
- [ ] Social features: Trek buddy matching
- [ ] Payment gateway integration

---

## 📝 License

This is a portfolio/demonstration project for AI Engineering interviews.

---

## 🙏 Acknowledgments

**Technologies**:
- LangChain & LangGraph by Anthropic/LangChain AI
- OpenAI for GPT models & embeddings
- FAISS by Meta Research
- HuggingFace for sentence-transformers
- scikit-learn & XGBoost for ML

**Sample Data**:
- Trek information inspired by real Himalayan treks
- Safety guidelines based on high-altitude mountaineering best practices

---

## 📧 Contact

**GitHub**: [sweta1233](https://github.com/sweta1233)  
**Live Demo**: [trekking-management-sand.vercel.app](https://trekking-management-sand.vercel.app)  
**Repository**: [github.com/sweta1233/Trekking-management-app](https://github.com/sweta1233/Trekking-management-app)

---

**⭐ Star this project if it helped you learn AI Engineering!**
