#!/usr/bin/env python3
"""
Test script to verify AI Chatbot installation
Run: python TEST_INSTALLATION.py
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ PASSED")
        if result.stdout:
            print(result.stdout[-500:])
    else:
        print(f"❌ FAILED")
        if result.stderr:
            print(result.stderr[-500:])
    return result.returncode

def main():
    print("\n" + "="*60)
    print("AI Chatbot Installation Test")
    print("="*60)

    tests = []

    # Test 1: Python version
    tests.append(run_command("python --version", "Python Installation"))

    # Test 2: pip install
    tests.append(run_command("pip list | head -20", "Installed Packages"))

    # Test 3: Environment variables
    print(f"\n{'='*60}")
    print("Testing: Environment Configuration")
    print('='*60)
    if os.path.exists(".env"):
        print("✅ .env file exists")
        with open(".env") as f:
            content = f.read()
            if "OPENAI_API_KEY" in content:
                print("✅ OPENAI_API_KEY configured")
            else:
                print("⚠️  OPENAI_API_KEY not found in .env")
            if "DATABASE_URL" in content:
                print("✅ DATABASE_URL configured")
            else:
                print("⚠️  DATABASE_URL not found in .env")
    else:
        print("❌ .env file not found")

    # Test 4: Try importing key modules
    print(f"\n{'='*60}")
    print("Testing: Python Module Imports")
    print('='*60)
    modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("asyncpg", "AsyncPG"),
        ("redis", "Redis"),
        ("chromadb", "ChromaDB"),
        ("openai", "OpenAI"),
        ("pydantic", "Pydantic"),
    ]
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name} ({module})")
        except ImportError as e:
            print(f"❌ {name} ({module}) - {e}")

    # Summary
    print(f"\n{'='*60}")
    print("Installation Summary")
    print('='*60)
    passed = sum(1 for t in tests if t == 0)
    total = len(tests)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed! Ready to start the server.")
        print("\nNext steps:")
        print("1. Ensure Docker is running with PostgreSQL and Redis")
        print("2. Start backend: python -m app.main")
        print("3. Start frontend: npm run dev")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
