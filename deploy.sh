#!/bin/bash
# TrekMate AI - Deployment Script
# This script commits and pushes all changes to GitHub
# which will automatically deploy to Vercel

echo "======================================"
echo "🏔️  TrekMate AI - Deployment Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📊 Checking git status..."
git status
echo ""

echo "📝 Staging all changes..."
git add .
echo "✅ All changes staged"
echo ""

echo "💾 Creating commit..."
git commit -m "Add TrekMate AI - Complete AI Engineering Portfolio Project

🚀 Live Demo: https://trekking-management-sand.vercel.app
📂 GitHub: https://github.com/sweta1233/Trekking-management-app
👤 Developer: @sweta1233

✨ Features Added:
- RAG Pipeline with LangChain, FAISS vector search, document chunking
- LangGraph Multi-Agent System with 8 specialized agents
- 11 AI API Endpoints (chat, RAG, recommendations, trip planning, etc.)
- Traditional ML Models (demand prediction with scikit-learn, XGBoost)
- Vector Database (FAISS) with semantic similarity search
- Embeddings service with multi-provider support
- Complete AI Chat Interface (Vue.js component)
- Comprehensive seed data with sample treks and documents
- Docker deployment setup with docker-compose
- Full documentation (README, guides, summaries)

🎨 UI Updates:
- Add project banner with GitHub and Live Demo buttons
- Add footer with project info, technologies, social links
- Update all documentation with deployment URLs
- Add responsive design for mobile devices

📚 Documentation:
- README.md - Complete project overview
- IMPLEMENTATION_SUMMARY.md - What was built
- QUICK_START.md - Quick start guide
- GET_STARTED.md - Getting started guide
- DEPLOYMENT_CHECKLIST.md - Deployment steps

🛠️ Technologies:
- Backend: Flask, SQLAlchemy, JWT, Celery
- AI/ML: LangChain, LangGraph, FAISS, OpenAI/Anthropic/Gemini
- ML: scikit-learn, XGBoost, pandas, numpy
- Frontend: Vue.js 3, Tailwind CSS, Axios
- Database: PostgreSQL/SQLite
- Deployment: Docker, Vercel

Co-Authored-By: Claude Code <noreply@anthropic.com>"

if [ $? -eq 0 ]; then
    echo "✅ Commit created successfully"
else
    echo "⚠️  Commit may have failed or there were no changes to commit"
fi
echo ""

echo "🚀 Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ Successfully pushed to GitHub!"
    echo "======================================"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Check GitHub: https://github.com/sweta1233/Trekking-management-app"
    echo "2. Wait 2-5 minutes for Vercel to deploy"
    echo "3. Visit: https://trekking-management-sand.vercel.app"
    echo "4. Verify project banner appears at top"
    echo "5. Verify footer appears at bottom"
    echo "6. Test GitHub and Live Demo buttons"
    echo ""
    echo "🎉 Deployment initiated successfully!"
else
    echo ""
    echo "❌ Push failed. Trying with upstream..."
    git push -u origin main

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Successfully pushed to GitHub!"
        echo ""
        echo "Visit: https://trekking-management-sand.vercel.app"
    else
        echo ""
        echo "❌ Push failed. Please check:"
        echo "1. Git credentials are configured"
        echo "2. Remote repository is accessible"
        echo "3. You have push access"
        echo ""
        echo "Try manually:"
        echo "  git pull origin main --rebase"
        echo "  git push origin main"
    fi
fi
