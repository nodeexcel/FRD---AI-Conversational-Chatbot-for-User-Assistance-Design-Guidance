# JWT Authentication Testing Guide

## Prerequisites

Install missing dependency:
```bash
pip install email-validator
```

---

## Testing with Frontend UI

### Step 1: Start Backend
```bash
cd backend
python -m uvicorn app.main:app --port 8001
```

### Step 2: Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### Step 3: Test in Browser

1. Open **http://localhost:5173**
2. You'll be redirected to `/login`
3. Click **"Sign up for free"** link
4. Fill the signup form:
   ```
   Name: Your Name
   Email: user@test.com
   Password: TestPass123
   Confirm: TestPass123
   ```
5. Click **Create Account**
6. You'll be redirected to the chat page with your user name displayed

---

## Testing with API (curl)

### 1. Register User
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "name": "Test User",
    "password": "TestPass123",
    "confirm_password": "TestPass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid-here",
    "email": "testuser@example.com",
    "name": "Test User",
    "is_active": true
  }
}
```

### 2. Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123"
  }'
```

### 3. Access Protected Chat API (with token)
```bash
# Replace TOKEN with the access_token from login response
curl -X POST http://localhost:8001/api/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"message": "Show me blue dresses"}'
```

### 4. Logout
```bash
curl -X POST http://localhost:8001/api/auth/logout
```

---

## Automated Test Script

Run the test script:
```bash
cd backend
python test_auth.py
```

This will test:
- ✅ User registration
- ✅ User login
- ✅ Protected endpoint access
- ✅ Logout
- ✅ Invalid login rejection

---

## Password Validation Rules

Password must have:
- ✅ At least 8 characters
- ✅ One uppercase letter (A-Z)
- ✅ One lowercase letter (a-z)
- ✅ One number (0-9)

---

## Database

Users are stored in PostgreSQL `users` table:
- id (UUID)
- email (unique)
- name
- hashed_password (bcrypt)
- is_active
- created_at
- updated_at
