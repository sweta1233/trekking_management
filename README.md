# 🏔️ TrekMate AI - Intelligent Trekking Management Platform

A production-grade full-stack trekking management application with **AI-powered features**, real-time trek tracking, and comprehensive management tools for administrators, staff, and trekkers.

🚀 **Live Demo**: [trekking-management-sand.vercel.app](https://trekking-management-sand.vercel.app)  
📂 **GitHub**: [github.com/sweta1233/trekking_management](https://github.com/sweta1233/trekking_management)  
👤 **Developer**: [@sweta1233](https://github.com/sweta1233)

---

## 🎯 Project Overview

TrekMate AI is a comprehensive trekking management platform featuring:

- **🤖 AI Assistant** - Powered by RAG, LangGraph, and Vector Search for intelligent trek recommendations
- **📍 Live Trek Tracking** - Real-time location, altitude, weather monitoring with ML predictions
- **📊 Admin Dashboard** - Complete management system for treks, staff, users, and bookings
- **👥 Staff Management** - Trek guide portal for managing participants and itineraries
- **🎯 User Portal** - Browse treks, book adventures, track progress, and access AI assistance

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip and npm installed

### 1. Backend Setup

```bash
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

# Create .env file
echo "SECRET_KEY=dev-secret-key" > .env
echo "JWT_SECRET_KEY=dev-jwt-secret" >> .env
echo "DATABASE_URL=sqlite:///instances/tma.db" >> .env

# Seed sample data (creates treks, users, documents)
python seeds.py

# Start backend
python app.py
```

✅ Backend runs at **http://localhost:5000**

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:5000/api" > .env

# Start frontend
npm run dev
```

✅ Frontend runs at **http://localhost:5173**

### 3. Login & Test

Open **http://localhost:5173** and login with:

**Admin Access:**
- Email: `admin@tma.com`
- Password: `Admin@123`

**User Access:**
- Email: `priya.sharma@example.com`
- Password: `Test@123`

**Staff Access:**
- Email: `rajesh.guide@example.com`
- Password: `Staff@123`

---

## 🛠️ Technology Stack

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Responsive Design** - Mobile-first approach

### Backend
- **Python 3.10+** - Core language
- **Flask** - REST API framework
- **SQLAlchemy** - ORM for database operations
- **JWT** - Secure authentication
- **Flask-Caching** - Performance optimization

### AI/ML Features (Optional)
- **LangChain** - Document processing and RAG pipeline
- **LangGraph** - Multi-agent orchestration
- **FAISS** - Vector database for semantic search
- **OpenAI / Anthropic / Gemini** - LLM providers (configurable)
- **scikit-learn / XGBoost** - Traditional ML models

### Database
- **SQLite** - Development
- **PostgreSQL** - Production (optional)

---

## 📊 Features by Role

### 👤 Users (Trekkers)
- ✅ Browse available treks with filtering
- ✅ Book treks and manage bookings
- ✅ View trekking history
- ✅ **🤖 AI Assistant** - Ask questions, get recommendations
- ✅ **📍 Live Trek Tracker** - Real-time progress monitoring
  - Current altitude, distance, time elapsed
  - Interactive route map with checkpoints
  - ML-powered predictions (ETA, weather, risk assessment)
  - Group member tracking
  - Real-time alerts
- ✅ Profile management
- ✅ Dashboard with statistics

### 👥 Staff (Trek Guides)
- ✅ View assigned treks
- ✅ Manage trek participants
- ✅ Update trek status
- ✅ **🤖 AI Assistant** - Access to all AI features
- ✅ **📍 Trek Tracker** - Monitor ongoing treks
- ✅ Profile management
- ✅ Dashboard with assigned treks

### 🔐 Administrators
- ✅ Complete trek management (create, edit, delete)
- ✅ User and staff management
- ✅ Booking oversight and approvals
- ✅ Revenue reports and analytics
- ✅ **🤖 AI Assistant** - Full AI capabilities
- ✅ **📍 Trek Tracker** - Monitor all active treks
- ✅ Advanced search and filtering
- ✅ System settings
- ✅ Comprehensive dashboard

---

## 🗄️ Database Schema

### Core Tables
- **users** - User accounts (admin, staff, user roles)
- **treks** - Trek information and details
- **bookings** - User trek reservations
- **reviews** - Trek reviews and ratings

### AI Features (Optional)
- **trek_documents** - Documents for RAG pipeline
- **document_chunks** - Chunked content for vector search
- **conversations** - AI chat history
- **ai_interaction_logs** - Analytics and observability

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Login (returns JWT token)

### Core Features
- `GET /api/treks` - List all treks with filters
- `GET /api/treks/:id` - Trek details
- `POST /api/treks` - Create trek (admin only)
- `PUT /api/treks/:id` - Update trek (admin only)
- `DELETE /api/treks/:id` - Delete trek (admin only)
- `POST /api/bookings` - Book a trek
- `GET /api/bookings` - User's bookings
- `POST /api/reviews` - Submit review
- `GET /api/dashboard/admin` - Admin dashboard data
- `GET /api/dashboard/staff` - Staff dashboard data
- `GET /api/dashboard/user` - User dashboard data

### AI Features (Optional)
- `POST /api/ai/chat` - AI chat conversation
- `POST /api/ai/recommend` - Personalized recommendations
- `POST /api/ai/rag/query` - RAG document Q&A
- `POST /api/ai/trip-planner` - AI itinerary generation
- `POST /api/ai/documents/upload` - Upload documents for RAG

---

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# Seed sample data
docker-compose exec backend python seeds.py

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Services:
- Backend: http://localhost:5000
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# Application
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Database
DATABASE_URL=sqlite:///instances/tma.db
# For PostgreSQL: postgresql://user:pass@localhost:5432/trekmate

# Optional: AI Features
LLM_PROVIDER=mock  # or openai, anthropic, gemini
EMBEDDING_PROVIDER=mock  # or openai, huggingface
OPENAI_API_KEY=your-openai-key  # if using OpenAI
```

### Frontend Environment Variables

Create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:5000/api
```

---

## 📁 Project Structure

```
TrekMate_AI/
├── backend/
│   ├── ai/                    # AI services (RAG, LangGraph, etc.)
│   ├── ml/                    # Traditional ML models
│   ├── models.py              # Database models
│   ├── routes.py              # Core API routes
│   ├── ai_routes.py           # AI API endpoints
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration
│   ├── seeds.py               # Sample data seeder
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/         # Admin components
│   │   │   ├── staff/         # Staff components
│   │   │   ├── user/          # User components
│   │   │   │   ├── AIAssistant.vue
│   │   │   │   ├── TrekTracker.vue
│   │   │   │   └── UserDashboard.vue
│   │   │   └── shared/        # Shared components
│   │   ├── router/            # Vue Router configuration
│   │   ├── services/          # API and auth services
│   │   └── App.vue            # Root component
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## 🧪 Testing the Application

### 1. Test Core Features
- Login with different roles (admin, staff, user)
- Browse and filter treks
- Create a booking as a user
- Approve booking as admin
- View dashboards for each role

### 2. Test AI Features (if configured)
- Navigate to AI Assistant (available for all roles)
- Ask: "Which trek is best for beginners?"
- Ask: "What should I pack for high altitude?"
- Test personalized recommendations

### 3. Test Live Trek Tracker
- Login as any role
- Navigate to Trek Tracker (for active bookings)
- Observe real-time updates:
  - Progress percentage
  - Altitude, distance, temperature
  - Interactive map
  - ML predictions

---

## 🔍 Troubleshooting

### Backend Won't Start

**Issue**: Port 5000 already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9
```

**Issue**: Module not found
```bash
# Ensure virtual environment is activated
# Should see (venv) in terminal prompt
pip install -r requirements.txt
```

### Frontend Won't Connect

**Issue**: Can't reach backend
- Check `VITE_API_BASE_URL` in `frontend/.env`
- Ensure backend is running at http://localhost:5000
- Check for CORS errors in browser console

### Database Issues

**Issue**: Database locked (SQLite)
```bash
# Stop backend, delete database, re-seed
rm backend/instances/tma.db
python seeds.py
```

---

## 🚀 Deployment

### Vercel (Frontend)
1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variable: `VITE_API_BASE_URL=<your-backend-url>/api`
4. Deploy

### Render (Backend)
1. Create new Web Service on Render
2. Connect GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && python app.py`
5. Add environment variables from `.env.example`
6. Deploy

---

## 📈 Key Features Highlights

### 1. Live Trek Tracking
Real-time monitoring system with:
- **Progress Visualization** - Circular progress indicator
- **Live Stats** - Altitude, time, distance, temperature
- **Interactive Map** - Canvas-based route with checkpoints
- **ML Predictions** - ETA, weather forecast, risk assessment, energy levels
- **Group Tracking** - Monitor all group members' status
- **Alerts System** - Weather and safety notifications

### 2. AI Assistant (Optional)
Intelligent assistance powered by:
- **RAG Pipeline** - Document-grounded answers with citations
- **LangGraph** - Multi-agent orchestration
- **Vector Search** - Semantic similarity matching
- **Personalized Recommendations** - Based on user profile and preferences
- **Trip Planning** - AI-generated itineraries

### 3. Role-Based Access Control
- **Admins**: Full system access and management
- **Staff**: Trek and participant management
- **Users**: Booking and personal tracking

---

## 📝 Sample Data

The `seeds.py` script creates:
- **5 diverse treks** (Easy to Expert difficulty)
- **1 admin account**
- **2 staff accounts** (trek guides)
- **4 user accounts** with varied profiles
- **Sample bookings and reviews**
- **2 trek guide documents** (if AI features enabled)

---

## 🔮 Future Enhancements

- [ ] Payment gateway integration
- [ ] Mobile app (React Native)
- [ ] Real-time weather API integration
- [ ] Multi-language support
- [ ] Social features (trek buddy matching)
- [ ] Advanced analytics and reporting
- [ ] Push notifications
- [ ] Offline mode for mobile

---

## 📄 License

This project is available for educational and portfolio purposes.

---

## 🙏 Acknowledgments

Built with modern web technologies and AI frameworks:
- Vue.js, Flask, SQLAlchemy
- LangChain, LangGraph (optional AI features)
- OpenAI, Anthropic, Google Gemini (optional LLM providers)
- FAISS, scikit-learn, XGBoost (optional ML features)

---

## 📧 Contact

**Developer**: [@sweta1233](https://github.com/sweta1233)  
**Live Demo**: [trekking-management-sand.vercel.app](https://trekking-management-sand.vercel.app)  
**Repository**: [github.com/sweta1233/trekking_management](https://github.com/sweta1233/trekking_management)

---

**⭐ Star this project if you found it helpful!**
