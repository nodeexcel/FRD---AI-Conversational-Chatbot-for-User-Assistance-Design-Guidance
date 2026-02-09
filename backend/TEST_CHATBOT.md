# AI Chatbot Testing Guide

## Prerequisites

Ensure the backend is running:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## Test 1: Health Check

```bash
curl -s http://localhost:8001/api/chat/health | python -m json.tool
```

**Expected Output:**
```json
{
    "status": "healthy",
    "nlu": {"status": "healthy", ...},
    "knowledge": {"status": "not_initialized", ...},
    "openai": {"status": "ok", "api_key_configured": true, "model": "gpt-4o"},
    "active_sessions": 0
}
```

---

## Test 2: Product Search (Database Query)

```bash
curl -X POST http://localhost:8001/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me blue dress products"}'
```

**Expected Intent:** `database_query`

---

## Test 3: Price Query

```bash
curl -X POST http://localhost:8001/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "What products are available under $100"}'
```

---

## Test 4: Intent Detection Only

```bash
curl -X POST http://localhost:8001/api/chat/intent \
  -H "Content-Type: application/json" \
  -d '{"message": "Find formal dresses for wedding"}'
```

---

## Test 5: Conversation History

```bash
curl http://localhost:8001/api/chat/history/{session_id}
```

Replace `{session_id}` with the session ID from previous responses.

---

## Test with Python Script

Create `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8001/api/chat"

def test_health():
    print("=== Test 1: Health Check ===")
    r = requests.get(f"{BASE_URL}/health")
    print(json.dumps(r.json(), indent=2))
    print()

def test_product_search():
    print("=== Test 2: Product Search ===")
    payload = {"message": "Show me blue dress products"}
    r = requests.post(f"{BASE_URL}/send", json=payload)
    data = r.json()
    print(f"Intent: {data.get('intent')}")
    print(f"Entities: {data.get('entities')}")
    print(f"Database Rows: {data.get('database_results', {}).get('row_count', 0)}")
    print()

def test_price_query():
    print("=== Test 3: Price Query ===")
    payload = {"message": "Find products under $100"}
    r = requests.post(f"{BASE_URL}/send", json=payload)
    data = r.json()
    print(f"Response: {data.get('response', '')[:200]}...")
    print()

def test_intent_detection():
    print("=== Test 4: Intent Detection ===")
    payload = {"message": "What is silk fabric care?"}
    r = requests.post(f"{BASE_URL}/intent", json=payload)
    print(json.dumps(r.json(), indent=2))
    print()

if __name__ == "__main__":
    test_health()
    test_product_search()
    test_price_query()
    test_intent_detection()
    print("=== All Tests Complete ===")
```

Run:
```bash
python test_api.py
```

---

## Test with Frontend

1. Start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

2. Open: **http://localhost:5173**

3. Type queries like:
   - "Show me blue dresses"
   - "What is the price range?"
   - "Find formal wear"

---

## Test with Swagger UI

Open browser: **http://localhost:8001/docs**

1. Expand `Chat` → `/api/chat/send`
2. Click "Try it out"
3. Enter JSON body:
   ```json
   {
     "message": "Show me elegant dresses",
     "session_id": "test-session-1"
   }
   ```
4. Click "Execute"
