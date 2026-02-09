#!/usr/bin/env python3
"""Test script for Chat API with RAG and ChromaDB."""
import asyncio
import sys
import os
import json
import httpx

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_chat_api():
    """Test the chat API endpoint."""
    BASE_URL = "http://localhost:8000"
    
    print("=" * 60)
    print("Chat API Test with RAG + ChromaDB")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n[Test 1] Health check...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return
    
    # Test 2: Send a chat message
    print("\n[Test 2] Sending chat message...")
    test_messages = [
        "Show me blue cotton dresses for summer",
        "What dresses do you have?",
        "How many products are in stock?",
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Query {i}: '{message}' ---")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/api/chat/send",
                    json={
                        "message": message,
                        "session_id": f"test-session-{i}",
                        "language": "en"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Success!")
                    print(f"  Intent: {data.get('intent', 'N/A')}")
                    print(f"  Response: {data.get('response', '')[:200]}...")
                    if data.get('sources'):
                        print(f"  Sources: {data.get('sources')}")
                    if data.get('database_results'):
                        db_results = data.get('database_results')
                        print(f"  DB Results: {db_results.get('row_count', 0)} rows")
                else:
                    print(f"✗ Failed with status {response.status_code}")
                    print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Test 3: Test RAG directly
    print("\n" + "=" * 60)
    print("Direct RAG Test")
    print("=" * 60)
    
    # Test RAG knowledge query
    print("\n[Test 3] Testing RAG knowledge query...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/chat/send",
                json={
                    "message": "Tell me about cotton fabric dresses",
                    "session_id": "rag-test"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ RAG Response:")
                print(f"  Intent: {data.get('intent', 'N/A')}")
                print(f"  Response: {data.get('response', '')[:300]}...")
            else:
                print(f"✗ RAG failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    print("Starting Chat API tests...")
    asyncio.run(test_chat_api())
