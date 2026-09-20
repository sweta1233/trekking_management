# 🚀 TrekMate AI - Quick Start Guide

🌐 **Live Demo**: [https://trekking-management-sand.vercel.app](https://trekking-management-sand.vercel.app)  
📂 **Source Code**: [https://github.com/sweta1233/Trekking-management-app](https://github.com/sweta1233/Trekking-management-app)  
👤 **By**: [@sweta1233](https://github.com/sweta1233)

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.10+ (`python --version`)
- ✅ Node.js 18+ (`node --version`)
- ✅ pip installed (`pip --version`)
- ✅ npm installed (`npm --version`)

Optional (for production features):
- Redis (for caching)
- PostgreSQL (for production database)

---

## 🎯 5-Minute Quick Start (Offline Mode)

This runs TrekMate AI with **mock providers** (no API keys needed) for instant testing.

### Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (offline mode)
echo "LLM_PROVIDER=mock" > .env
echo "EMBEDDING_PROVIDER=mock" >> .env
echo "SECRET_KEY=dev-secret-key" >> .env
echo "JWT_SECRET_KEY=dev-jwt-secret" >> .env

# Seed sample data (creates treks, documents, users)
python seeds.py

# Start backend
python app.py
```

✅ Backend should be running at **http://localhost:5000**

### Step 2: Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:5000/api" > .env

# Start frontend
npm run dev
```

✅ Frontend should be running at **http://localhost:5173**

### Step 3: Login & Test

1. Open browser: **http://localhost:5173**
2. Login with:
   - Email: `priya.sharma@example.com`
   - Password: `Test@123`
3. Navigate to **AI Assistant** (should be in the user menu)
4. Try asking:
   - "Which trek is best for beginners?"
   - "What should I pack for Kedarkantha?"
   - "How to prevent altitude sickness?"

---

## 🔥 Full AI Setup (With Real LLMs)

### Option 1: OpenAI (Recommended for Start)

```bash
# In backend/.env, set:
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

**Get API Key**: https://platform.openai.com/api-keys

**Cost Estimate**:
- ~500 queries: $2-3 USD
- text-embedding-3-small: very cheap ($0.020 / 1M tokens)

### Option 2: Anthropic (Claude)

```bash
LLM_PROVIDER=anthropic
EMBEDDING_PROVIDER=openai  # Use OpenAI for embeddings
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
OPENAI_API_KEY=your-openai-key-for-embeddings
```

**Get API Key**: https://console.anthropic.com/

### Option 3: Google Gemini (Free Tier)

```bash
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=openai  # Use OpenAI for embeddings
GOOGLE_API_KEY=your-google-api-key
GEMINI_MODEL=gemini-1.5-flash
OPENAI_API_KEY=your-openai-key-for-embeddings
```

**Get API Key**: https://makersuite.google.com/app/apikey

---

## 🧪 Testing AI Features

### Test 1: RAG Document Q&A

```bash
# Login and get JWT token first
TOKEN="your-jwt-token-here"

# Query RAG system
curl -X POST http://localhost:5000/api/ai/rag/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the symptoms of altitude sickness?",
    "trek_id": 1
  }'
```

**Expected**: Answer with source citations (document name, page number, section)

### Test 2: AI Chat (LangGraph)

```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Which trek is best for beginners in winter?",
    "session_id": "test_session_123"
  }'
```

**Expected**: Structured response with trek recommendations, intent classification, tool calls

### Test 3: Personalized Recommendations

```bash
curl -X POST http://localhost:5000/api/ai/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "experience_level": "Beginner",
    "budget": 15000,
    "interests": "snow trekking with lakes",
    "top_n": 3
  }'
```

**Expected**: Top 3 treks with match scores and reasons

### Test 4: Upload Document for RAG

```bash
# Create a test document
echo "# Test Trek Guide

This is a test safety guide for high altitude trekking.

## Altitude Sickness Prevention
- Ascend slowly
- Drink 4L water daily
- Watch for symptoms" > test_guide.txt

# Upload
curl -X POST http://localhost:5000/api/ai/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_guide.txt" \
  -F "title=Test Safety Guide" \
  -F "category=safety" \
  -F "trek_id=1"
```

**Expected**: Document indexed with chunk count

### Test 5: Semantic Search

```bash
curl -X POST http://localhost:5000/api/ai/search/semantic \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "peaceful forest trek with mountain views",
    "top_k": 3
  }'
```

**Expected**: Treks matching semantic meaning (not keyword match)

---

## 🐳 Docker Quick Start

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Seed data (first time only)
docker-compose exec backend python seeds.py

# Access application
# Frontend: http://localhost:5173
# Backend: http://localhost:5000
# PostgreSQL: localhost:5432
# Redis: localhost:6379

# Stop services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

---

## 🔍 Verification Checklist

### Backend Health Check
```bash
curl http://localhost:5000/api/health
```
✅ Should return: `{"status": "healthy", "service": "TMA Backend"}`

### Database Check
```bash
# In backend directory with activated venv
python -c "from app import create_app; from models import db, Trek; app = create_app(); app.app_context().push(); print(f'Treks in DB: {Trek.query.count()}')"
```
✅ Should show: `Treks in DB: 5` (after running seeds.py)

### Vector Store Check
```bash
ls -la backend/instances/faiss_index/
```
✅ Should have FAISS index files if documents were indexed

### Documents Check
```bash
ls -la backend/instances/documents/
```
✅ Should have .txt files (kedarkantha_complete_guide.txt, high_altitude_safety_manual.txt)

---

## 📊 Admin Access

Login as admin to see all features:
- Email: `admin@tma.com`
- Password: `Admin@123`

Admin can access:
- `/admin/dashboard` - Overview & analytics
- `/admin/treks` - Manage treks
- `/admin/users` - Manage users
- Navigate to AI Analytics (need to add route in admin menu)

---

## 🎓 Sample Users (Created by seeds.py)

| Email | Password | Experience | Fitness |
|-------|----------|------------|---------|
| priya.sharma@example.com | Test@123 | Beginner | Moderate |
| rajesh.kumar@example.com | Test@123 | Intermediate | High |
| ananya.reddy@example.com | Test@123 | Advanced | Athletic |
| vikram.singh@example.com | Test@123 | Expert | Athletic |

---

## 🛠️ Troubleshooting

### Issue: "Module not found" errors
**Solution**: Make sure virtual environment is activated
```bash
# Check if venv is active (should see (venv) in prompt)
which python  # Should point to venv/bin/python
pip install -r requirements.txt
```

### Issue: Port 5000 already in use
**Solution**: Kill existing process or change port
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9

# Or change port
PORT=5001 python app.py
```

### Issue: Frontend can't connect to backend
**Solution**: Check CORS and API URL
```bash
# In frontend/.env
VITE_API_BASE_URL=http://localhost:5000/api

# Restart frontend
npm run dev
```

### Issue: AI features return errors with mock provider
**Solution**: This is expected - mock provider gives generic responses
- For full AI: Set real API keys in backend/.env
- For testing: Mock responses are intentionally simple

### Issue: Database locked (SQLite)
**Solution**: Close all connections
```bash
# Stop backend
# Delete database file
rm backend/instances/tma.db

# Re-run seeds
python seeds.py
```

### Issue: Import errors for LangChain/LangGraph
**Solution**: Reinstall AI dependencies
```bash
pip install langchain==0.3.0 langgraph==0.2.28 langchain-community langchain-text-splitters
```

---

## 🎯 Next Steps After Quick Start

1. **Explore AI Chat Interface**
   - Try different question types
   - Check source citations in RAG responses
   - View conversation history

2. **Test Recommendation Engine**
   - Update your user profile (fitness, experience)
   - Ask for recommendations
   - See match scores and reasons

3. **Upload Custom Documents**
   - Create a PDF or TXT with trek information
   - Upload via API or (future) admin interface
   - Query it with RAG

4. **Check Admin Analytics**
   - View AI usage metrics
   - Track token consumption
   - Monitor latency

5. **Customize Configuration**
   - Experiment with different LLM providers
   - Adjust RAG parameters (chunk size, top-k)
   - Try different embedding models

---

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **API Reference**: See README API Endpoints section
- **Architecture Diagrams**: See README Architecture section

---

## 🚨 Important Notes

### Security
- ⚠️ Never commit `.env` file with real API keys
- ⚠️ Change default passwords in production
- ⚠️ Use environment variables in production, not .env file

### Cost Management
- 💰 Mock provider is free (offline)
- 💰 OpenAI gpt-4o-mini is cheap (~$0.15 per 1M input tokens)
- 💰 Monitor usage in admin analytics
- 💰 Set OpenAI usage limits at platform.openai.com

### Development Mode
- 🔧 SQLite is fine for development
- 🔧 SimpleCache works without Redis
- 🔧 Mock providers work without API keys

### Production Deployment
- 🚀 Use PostgreSQL for database
- 🚀 Use Redis for caching
- 🚀 Set proper CORS origins
- 🚀 Use gunicorn with multiple workers
- 🚀 Enable HTTPS
- 🚀 Set up monitoring/logging

---

## ✅ Success Criteria

You've successfully set up TrekMate AI when:

1. ✅ Backend responds at http://localhost:5000/api/health
2. ✅ Frontend loads at http://localhost:5173
3. ✅ You can login with test credentials
4. ✅ AI Assistant page loads without errors
5. ✅ Asking questions returns responses (even if generic with mock provider)
6. ✅ Seeds script created 5 treks and 2 documents
7. ✅ Admin dashboard shows statistics

---

## 🎉 You're Ready!

Your TrekMate AI platform is now running. You have:
- ✅ Complete RAG pipeline with vector search
- ✅ LangGraph multi-agent orchestration
- ✅ Personalized recommendations
- ✅ Traditional ML integration
- ✅ Full-stack authentication
- ✅ Production-ready architecture

**Now go build something amazing! 🚀**
