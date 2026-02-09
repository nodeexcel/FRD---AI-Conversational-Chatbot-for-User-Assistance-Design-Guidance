# End-to-End Testing Guide: Resume Upload & RAG Q&A

This guide provides step-by-step instructions to test the document upload and RAG-based Q&A functionality.

## Prerequisites

### 1. Start Docker Services
```bash
cd backend
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- ChromaDB (port 8000)
- Redis (port 6379)

### 2. Start the Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start the Frontend
```bash
cd frontend
npm run dev
```

---

## Testing Steps

### Step 1: Register a New User

**Option A: Via Frontend**
1. Open browser at `http://localhost:5173`
2. Click "Sign Up"
3. Fill in email, password, and name
4. Click "Create Account"

**Option B: Via API**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "name": "Test User"
  }'
```

### Step 2: Login and Get Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

**Save the `access_token` for subsequent requests.**

### Step 3: Upload a Resume

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/resume.pdf" \
  -F "document_type=resume"
```

**Expected Response:**
```json
{
  "id": "document-uuid",
  "name": "resume.pdf",
  "document_type": "resume",
  "status": "processing",
  "chunk_count": 0,
  "created_at": "2024-01-01T00:00:00"
}
```

**Note:** The document will be:
1. Extracted for text
2. Chunked into smaller pieces
3. Indexed into ChromaDB with embeddings

### Step 4: Verify Document is Indexed

```bash
curl -X GET http://localhost:8000/api/v1/documents/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "documents": [
    {
      "id": "document-uuid",
      "name": "resume.pdf",
      "status": "indexed",
      "chunk_count": 15,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1
}
```

### Step 5: Query the Resume via Chat

Ask questions about your resume:

```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What skills are mentioned in my resume?",
    "session_id": "test-session-001"
  }'
```

**Expected Response:**
```json
{
  "response": "Based on your resume, the following skills are mentioned:\n\n1. Python Programming\n2. Machine Learning\n3. Data Analysis\n...",
  "session_id": "test-session-001",
  "intent": "knowledge_query",
  "sources": ["resume.pdf"],
  "products": []
}
```

### Example Questions to Try:

1. **Skills:**
   ```json
   {"message": "What technical skills do I have?"}
   ```

2. **Work Experience:**
   ```json
   {"message": "What is my work experience?"}
   ```

3. **Education:**
   ```json
   {"message": "What is my educational background?"}
   ```

4. **Summary:**
   ```json
   {"message": "Summarize my resume"}
   ```

5. **Projects:**
   ```json
   {"message": "What projects have I worked on?"}
   ```

---

## Monitoring Logs

### Watch Backend Logs for RAG Operations

```bash
# Look for these log prefixes:
# [VECTOR] - ChromaDB operations (search, index)
# [CHAT-RAG] - RAG query/response
# [RECTOR] - Document processing
# [RAG] - RAG agent processing
```

### Example Log Output:
```
[VECTOR] Searching collection 'knowledge_base' for 10 results
[VECTOR] Query texts: ['What skills are mentioned in my resume?']
[VECTOR] Collection ID: abc-123-def
[RECTOR] Extracted 2500 characters from resume.pdf
[RECTOR] Created 15 chunks from document
[VECTOR] Successfully added 15 documents to ChromaDB
[CHAT-RAG] Query: 'What skills are mentioned in my resume?'
[CHAT-RAG] Result: success=True, sources=['resume.pdf']
[CHAT-RAG] Response preview: Based on your resume, the following skills are mentioned:...
```

---

## Troubleshooting

### Issue 1: "No documents found" in RAG

**Check:**
1. Is ChromaDB running? `docker ps`
2. Is the document status "indexed"?
3. Check chunk_count > 0

**Fix:**
```bash
# Restart ChromaDB
docker-compose restart chromadb
```

### Issue 2: "401 Unauthorized"

**Cause:** Token expired or invalid

**Fix:**
1. Re-login to get new token
2. Check Authorization header format: `Bearer YOUR_TOKEN`

### Issue 3: Upload Fails

**Check:**
1. File format (PDF, DOCX, TXT supported)
2. File size (max 10MB)
3. Network connectivity

### Issue 4: Empty Response from Chat

**Check:**
1. Document is indexed (chunk_count > 0)
2. Query contains relevant keywords
3. Check logs for `[VECTOR]` errors

---

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Login and get token |
| `/api/v1/documents/upload` | POST | Upload document |
| `/api/v1/documents/` | GET | List user documents |
| `/api/v1/chat/send` | POST | Send chat message |

---

## Testing with Postman/Insomnia

1. **Create a Collection** for your API requests
2. **Add Authorization** to all requests:
   - Type: Bearer Token
   - Token: Paste your login response token
3. **Test Upload:**
   - POST `/api/v1/documents/upload`
   - Body: form-data with `file` and `document_type`
4. **Test Chat:**
   - POST `/api/v1/chat/send`
   - Body: raw JSON with `message` and `session_id`
