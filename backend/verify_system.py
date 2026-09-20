#!/usr/bin/env python3
"""
TrekMate AI - System Verification Script

Run this script to verify that all components are properly set up.
Usage: python verify_system.py
"""

import os
import sys
import subprocess
from pathlib import Path

BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print(f"{text}")
    print(f"{'=' * 60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def check_python_version():
    """Check Python version"""
    print_header("1. Checking Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print_header("2. Checking Python Dependencies")

    required_packages = [
        "flask",
        "langchain",
        "langgraph",
        "openai",
        "anthropic",
        "faiss",
        "sentence_transformers",
        "sklearn",
        "pandas",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NOT INSTALLED")
            missing.append(package)

    if missing:
        print_warning(f"\nMissing packages: {', '.join(missing)}")
        print_warning("Run: pip install -r requirements.txt")
        return False
    return True

def check_directories():
    """Check if required directories exist"""
    print_header("3. Checking Directory Structure")

    dirs = [
        BACKEND_DIR / "ai",
        BACKEND_DIR / "ml",
        BACKEND_DIR / "evaluation",
        BACKEND_DIR / "knowledge_base",
        BACKEND_DIR / "instances",
        BACKEND_DIR / "instances" / "documents",
        BACKEND_DIR / "instances" / "faiss_index",
        FRONTEND_DIR / "src" / "components" / "user",
    ]

    all_exist = True
    for dir_path in dirs:
        if dir_path.exists():
            print_success(f"{dir_path.relative_to(PROJECT_ROOT)}")
        else:
            print_error(f"{dir_path.relative_to(PROJECT_ROOT)} - MISSING")
            all_exist = False

    return all_exist

def check_env_file():
    """Check if .env file exists"""
    print_header("4. Checking Environment Configuration")

    env_path = BACKEND_DIR / ".env"
    env_example_path = BACKEND_DIR / ".env.example"

    if env_path.exists():
        print_success(".env file exists")

        # Check for critical keys
        with open(env_path) as f:
            content = f.read()

        if "LLM_PROVIDER" in content:
            print_success("LLM_PROVIDER configured")
        else:
            print_warning("LLM_PROVIDER not set")

        if "SECRET_KEY" in content:
            print_success("SECRET_KEY configured")
        else:
            print_warning("SECRET_KEY not set")

        return True
    else:
        print_error(".env file missing")
        if env_example_path.exists():
            print_warning("Copy .env.example to .env and configure it")
        return False

def check_database():
    """Check database setup"""
    print_header("5. Checking Database")

    try:
        from app import create_app
        from models import db, Trek, User, TrekDocument

        app = create_app()
        with app.app_context():
            trek_count = Trek.query.count()
            user_count = User.query.count()
            doc_count = TrekDocument.query.count()

            print_success(f"Database initialized")
            print_success(f"Treks: {trek_count}")
            print_success(f"Users: {user_count}")
            print_success(f"Documents: {doc_count}")

            if trek_count == 0:
                print_warning("No treks found. Run: python seeds.py")
                return False

            return True
    except Exception as e:
        print_error(f"Database error: {e}")
        return False

def check_ai_services():
    """Check AI services"""
    print_header("6. Checking AI Services")

    try:
        from ai.agent_graph import get_agent_workflow
        from ai.rag_service import get_rag_service
        from ai.recommendation_engine import RecommendationEngine
        from ai.vector_store import get_vector_store

        print_success("LangGraph Agent Workflow")
        print_success("RAG Service")
        print_success("Recommendation Engine")
        print_success("Vector Store")

        return True
    except Exception as e:
        print_error(f"AI services error: {e}")
        return False

def check_vector_store():
    """Check if vector store is populated"""
    print_header("7. Checking Vector Store")

    faiss_dir = BACKEND_DIR / "instances" / "faiss_index"
    if faiss_dir.exists() and any(faiss_dir.iterdir()):
        print_success("FAISS index exists")
        return True
    else:
        print_warning("FAISS index empty. Documents may not be indexed yet.")
        print_warning("Run: python seeds.py to index sample documents")
        return False

def check_frontend():
    """Check frontend setup"""
    print_header("8. Checking Frontend")

    if not FRONTEND_DIR.exists():
        print_error("Frontend directory missing")
        return False

    package_json = FRONTEND_DIR / "package.json"
    if package_json.exists():
        print_success("package.json exists")
    else:
        print_error("package.json missing")
        return False

    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists():
        print_success("node_modules exists")
    else:
        print_warning("node_modules missing. Run: npm install")
        return False

    ai_component = FRONTEND_DIR / "src" / "components" / "user" / "AIAssistant.vue"
    if ai_component.exists():
        print_success("AI Assistant component exists")
    else:
        print_error("AI Assistant component missing")
        return False

    return True

def print_next_steps():
    """Print next steps"""
    print_header("Next Steps")

    print(f"""
{Colors.BLUE}To run TrekMate AI:{Colors.END}

1. {Colors.GREEN}Start Backend:{Colors.END}
   cd backend
   python app.py

2. {Colors.GREEN}Start Frontend (new terminal):{Colors.END}
   cd frontend
   npm run dev

3. {Colors.GREEN}Access Application:{Colors.END}
   Frontend: http://localhost:5173
   Backend:  http://localhost:5000

4. {Colors.GREEN}Login:{Colors.END}
   Email: priya.sharma@example.com
   Password: Test@123

5. {Colors.GREEN}Test AI Features:{Colors.END}
   - Navigate to AI Assistant
   - Ask: "Which trek is best for beginners?"
   - Check source citations in responses

{Colors.BLUE}Documentation:{Colors.END}
   - README.md - Complete documentation
   - QUICK_START.md - Quick start guide
   - IMPLEMENTATION_SUMMARY.md - What was built

{Colors.BLUE}Seed Data:{Colors.END}
   If you haven't run seeds.py yet:
   python seeds.py

{Colors.BLUE}Docker (Alternative):{Colors.END}
   docker-compose up -d
""")

def main():
    print(f"""
{Colors.BLUE}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           TrekMate AI - System Verification               ║
║                                                           ║
║   Checking setup for RAG, LangGraph, Vector DB,          ║
║   LangChain, and Traditional ML components               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.END}
""")

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directory Structure", check_directories),
        ("Environment Config", check_env_file),
        ("Database", check_database),
        ("AI Services", check_ai_services),
        ("Vector Store", check_vector_store),
        ("Frontend", check_frontend),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error checking {name}: {e}")
            results.append((name, False))

    # Summary
    print_header("Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        if result:
            print_success(name)
        else:
            print_error(name)

    print(f"\n{Colors.BLUE}Checks passed: {passed}/{total}{Colors.END}\n")

    if passed == total:
        print(f"{Colors.GREEN}✓ All checks passed! TrekMate AI is ready to run.{Colors.END}")
    elif passed >= total * 0.7:
        print(f"{Colors.YELLOW}⚠ Most checks passed. Review warnings above.{Colors.END}")
    else:
        print(f"{Colors.RED}✗ Several checks failed. Please fix the issues above.{Colors.END}")

    print_next_steps()

if __name__ == "__main__":
    main()
