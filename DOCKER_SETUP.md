# Complete Docker Setup Guide (From Scratch)

## Prerequisites

You only need **Docker Desktop** installed on Windows.

---

## Step 1: Open Command Prompt

1. Press `Windows + R`
2. Type `cmd`
3. Press `Enter`

---

## Step 2: Navigate to Project Directory

```cmd
cd c:\Users\PRATEEK SARASWAT\OneDrive\Desktop\Excellence Technologies\CLIENT-AI-PROJECT
```

**Note**: If your path has spaces, use quotes:
```cmd
cd "c:\Users\PRATEEK SARASWAT\OneDrive\Desktop\Excellence Technologies\CLIENT-AI-PROJECT"
```

Verify you're in the right folder:
```cmd
dir
```
You should see files like `docker-compose.yml`, `backend/`, `frontend/`

---

## Step 3: Create .env File

Create a file named `.env` in the project root with this exact content:

```env
# Database
POSTGRES_USER=chatbot
POSTGRES_PASSWORD=chatbot_secret
POSTGRES_DB=chatbot_db

# Redis
REDIS_URL=redis://redis:6379/0

# Vector Database (Weaviate)
WEAVIATE_URL=http://weaviate:8080

# MongoDB
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=admin_secret
MONGO_DB=chatbot_logs
MONGO_URL=mongodb://admin:admin_secret@mongodb:27017/chatbot_logs?authSource=admin

# MinIO (File Storage)
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=admin_secret

# Application Settings
DEBUG=true
LOG_LEVEL=INFO

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

**How to create .env file:**
```cmd
notepad .env
```
Paste the content above, save, and exit.

---

## Step 4: Create backend/.env File

Create a file named `.env` inside the `backend` folder:

```env
DATABASE_URL=postgresql+asyncpg://chatbot:chatbot_secret@postgres:5432/chatbot_db
REDIS_URL=redis://redis:6379/0
WEAVIATE_URL=http://weaviate:8080
ELASTICSEARCH_URL=http://elasticsearch:9200
MONGO_URL=mongodb://admin:admin_secret@mongodb:27017/chatbot_logs?authSource=admin
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=admin_secret
DEBUG=true
LOG_LEVEL=INFO
```

**Create it:**
```cmd
cd backend
notepad .env
```
Paste, save, exit.

---

## Step 5: Start Docker Services

```cmd
docker-compose up -d
```

**Expected output:**
```
[+] Running 7/7
 ✔ Network chatbot_network   Created
 ✔ Container chatbot_elasticsearch  Started
 ✔ Container chatbot_mongodb        Started
 ✔ Container chatbot_minio          Started
 ✔ Container chatbot_postgres       Started
 ✔ Container chatbot_redis          Started
 ✔ Container chatbot_weaviate       Started
```

---

## Step 6: Verify Services are Running

```cmd
docker ps
```

You should see:
| CONTAINER ID | IMAGE | COMMAND | STATUS | PORTS |
|--------------|-------|---------|--------|-------|
| xxx | postgres:15 | docker-entrypoint.sh | Up | 0.0.0.0:5432->5432/tcp |
| xxx | redis:7 | docker-entrypoint.sh | Up | 0.0.0.0:6379->6379/tcp |
| xxx | weaviate:latest | /bin/weaviate | Up | 0.0.0.0:8080->8080/tcp |

---

## Step 7: Initialize Database

```cmd
docker exec -i chatbot_postgres psql -U chatbot -d chatbot_db < backend/init-scripts/01-init.sql
```

**Expected output:**
```
CREATE EXTENSION
CREATE TABLE
CREATE TABLE
...
INSERT 0 1
INSERT 0 1
```

---

## Step 8: Verify Database

```cmd
docker exec -it chatbot_postgres psql -U chatbot -d chatbot_db
```

In psql prompt, type:
```sql
\dt
```

Expected output:
```
              List of relations
 Schema |      Name       | Type  |  Owner
--------+----------------+-------+----------
 public | chat_sessions  | table | chatbot
 public | fabrics       | table | chatbot
 public | feedback      | table | chatbot
 public | messages      | table | chatbot
 public | products      | table | chatbot
 public | recommendations | table | chatbot
 public | user_preferences | table | chatbot
 public | users         | table | chatbot
(8 rows)
```

Exit psql:
```sql
\q
```

---

## Step 9: Install Python (For Backend)

1. Download Python from: https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check ✅ "Add Python to PATH"
4. Click "Install Now"

Verify:
```cmd
python --version
```

Should show: `Python 3.11.x`

---

## Step 10: Install Node.js (For Frontend)

1. Download from: https://nodejs.org (LTS version)
2. Run the installer
3. Keep all default options

Verify:
```cmd
node --version
npm --version
```

---

## Step 11: Setup Backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**This will take 2-5 minutes** (installs FastAPI, LangChain, etc.)

---

## Step 12: Start Backend

```cmd
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Database connection: healthy
```

**Keep this terminal open!**

---

## Step 13: Setup Frontend (New Terminal)

Open a **new** Command Prompt:
```cmd
cd frontend
npm install
npm run dev
```

**This will take 2-5 minutes** (installs React, Redux, etc.)

---

## Step 14: Access the Application

**Frontend:** http://localhost:3000
**Backend API:** http://localhost:8000
**API Docs:** http://localhost:8000/api/docs

---

## Quick Reference Commands

| Action | Command |
|--------|---------|
| Start all services | `docker-compose up -d` |
| Stop all services | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Restart a service | `docker-compose restart postgres` |
| Reset everything | `docker-compose down -v && docker-compose up -d` |
| Check running containers | `docker ps` |
| Stop backend | `Ctrl+C` (in backend terminal) |
| Start backend | `cd backend && venv\Scripts\activate && uvicorn app.main:app --reload` |
| Stop frontend | `Ctrl+C` (in frontend terminal) |
| Start frontend | `cd frontend && npm run dev` |

---

## Troubleshooting

### "docker: command not found"
Docker Desktop is not running. Start Docker Desktop from Start Menu.

### "Port already in use"
Something else is using the port:
```cmd
netstat -ano | findstr :5432
```
Find the PID and end the task, or change the port in docker-compose.yml.

### "Connection refused" to database
Wait 30 seconds for Docker to fully start, then try again.

### Python not recognized
Reinstall Python and check "Add Python to PATH".

### npm install fails
Delete `node_modules` folder and try again:
```cmd
cd frontend
rmdir /s node_modules
npm install
```

---

## What's Happening

1. **Docker** creates 7 isolated containers:
   - PostgreSQL (database)
   - Redis (caching)
   - Weaviate (AI vector search)
   - Elasticsearch (search)
   - MongoDB (logs)
   - MinIO (file storage)

2. **Backend** connects to these services and provides API

3. **Frontend** connects to backend and shows the chat UI

Everything stays running until you run `docker-compose down`!
