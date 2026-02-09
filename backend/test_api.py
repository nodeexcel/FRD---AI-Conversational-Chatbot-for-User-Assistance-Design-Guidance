#!/usr/bin/env python3
"""
Quick Test Script for AI Chatbot API
Run: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/chat"

def test_health():
    print("=" * 50)
    print("Test 1: Health Check")
    print("=" * 50)
    r = requests.get(f"{BASE_URL}/health")
    data = r.json()
    print(f"Status: {data.get('status')}")
    print(f"NLU: {data.get('nlu', {}).get('status')}")
    print(f"OpenAI: {data.get('openai', {}).get('status')}")
    print()

def test_product_search():
    print("=" * 50)
    print("Test 2: Product Search (Blue Dresses)")
    print("=" * 50)
    payload = {"message": "Show me blue dress products"}
    r = requests.post(f"{BASE_URL}/send", json=payload)
    data = r.json()
    print(f"Intent: {data.get('intent')}")
    print(f"Entities: {data.get('entities')}")
    print(f"Session: {data.get('session_id')}")
    rows = data.get('database_results', {}).get('row_count', 0)
    print(f"Products Found: {rows}")
    print(f"SQL Query: {data.get('database_results', {}).get('sql_query', 'N/A')}")
    print()

def test_price_query():
    print("=" * 50)
    print("Test 3: Price Query (Under $100)")
    print("=" * 50)
    payload = {"message": "Find products under $100"}
    r = requests.post(f"{BASE_URL}/send", json=payload)
    data = r.json()
    print(f"Intent: {data.get('intent')}")
    print(f"Response: {data.get('response', '')[:150]}...")
    print()

def test_intent_detection():
    print("=" * 50)
    print("Test 4: Intent Detection")
    print("=" * 50)
    payload = {"message": "What is silk fabric and how to care for it?"}
    r = requests.post(f"{BASE_URL}/intent", json=payload)
    data = r.json()
    print(f"Intent: {data.get('intent')}")
    print(f"Confidence: {data.get('confidence')}")
    print(f"Entities: {data.get('entities')}")
    print()

def test_formal_dress_query():
    print("=" * 50)
    print("Test 5: Formal Dress Query")
    print("=" * 50)
    payload = {"message": "Find formal dresses for wedding"}
    r = requests.post(f"{BASE_URL}/send", json=payload)
    data = r.json()
    print(f"Intent: {data.get('intent')}")
    print(f"Response: {data.get('response', '')[:150]}...")
    print()

def main():
    print("\n" + "=" * 50)
    print("AI Chatbot API Test Suite")
    print("=" * 50 + "\n")

    try:
        test_health()
        test_product_search()
        test_price_query()
        test_intent_detection()
        test_formal_dress_query()

        print("=" * 50)
        print("All Tests Complete!")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API at " + BASE_URL)
        print("Make sure the backend is running: python -m uvicorn app.main:app --port 8001")

if __name__ == "__main__":
    main()
