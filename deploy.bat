@echo off
REM TrekMate AI - Deployment Script for Windows
REM This script commits and pushes all changes to GitHub

echo ======================================
echo 🏔️  TrekMate AI - Deployment Script
echo ======================================
echo.

REM Check if we're in the right directory
if not exist "README.md" (
    echo ❌ Error: Please run this script from the project root directory
    exit /b 1
)

echo 📊 Checking git status...
git status
echo.

echo 📝 Staging all changes...
git add .
echo ✅ All changes staged
echo.

echo 💾 Creating commit...
git commit -m "Add TrekMate AI - Complete AI Engineering Portfolio Project" -m "" -m "🚀 Live Demo: https://trekking-management-sand.vercel.app" -m "📂 GitHub: https://github.com/sweta1233/Trekking-management-app" -m "👤 Developer: @sweta1233" -m "" -m "✨ Features Added:" -m "- RAG Pipeline with LangChain, FAISS vector search, document chunking" -m "- LangGraph Multi-Agent System with 8 specialized agents" -m "- 11 AI API Endpoints (chat, RAG, recommendations, trip planning, etc.)" -m "- Traditional ML Models (demand prediction with scikit-learn, XGBoost)" -m "- Vector Database (FAISS) with semantic similarity search" -m "- Embeddings service with multi-provider support" -m "- Complete AI Chat Interface (Vue.js component)" -m "- Comprehensive seed data with sample treks and documents" -m "- Docker deployment setup with docker-compose" -m "- Full documentation (README, guides, summaries)" -m "" -m "🎨 UI Updates:" -m "- Add project banner with GitHub and Live Demo buttons" -m "- Add footer with project info, technologies, social links" -m "- Update all documentation with deployment URLs" -m "- Add responsive design for mobile devices" -m "" -m "Co-Authored-By: Claude Code <noreply@anthropic.com>"

if %errorlevel% equ 0 (
    echo ✅ Commit created successfully
) else (
    echo ⚠️  Commit may have failed or there were no changes to commit
)
echo.

echo 🚀 Pushing to GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo ✅ Successfully pushed to GitHub!
    echo ======================================
    echo.
    echo 📋 Next Steps:
    echo 1. Check GitHub: https://github.com/sweta1233/Trekking-management-app
    echo 2. Wait 2-5 minutes for Vercel to deploy
    echo 3. Visit: https://trekking-management-sand.vercel.app
    echo 4. Verify project banner appears at top
    echo 5. Verify footer appears at bottom
    echo 6. Test GitHub and Live Demo buttons
    echo.
    echo 🎉 Deployment initiated successfully!
) else (
    echo.
    echo ❌ Push failed. Trying with upstream...
    git push -u origin main

    if %errorlevel% equ 0 (
        echo.
        echo ✅ Successfully pushed to GitHub!
        echo.
        echo Visit: https://trekking-management-sand.vercel.app
    ) else (
        echo.
        echo ❌ Push failed. Please check:
        echo 1. Git credentials are configured
        echo 2. Remote repository is accessible
        echo 3. You have push access
        echo.
        echo Try manually:
        echo   git pull origin main --rebase
        echo   git push origin main
    )
)

pause
