# AI Conversational Chatbot - Installation Guide

## Prerequisites

### System Requirements
- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL 14+
- Redis 7+
- 8GB RAM (16GB recommended)
- 10GB disk space

## Installation Steps

### 1. Clone and Setup

```bash
# Navigate to project directory
cd "c:/Users/PRATEEK SARASWAT/OneDrive/Desktop/Excellence Technologies/CLIENT-AI-PROJECT"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Environment Configuration

Create `.env` file in backend directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/chatbot_db

# Redis Configuration
REDIS_URL=redis://localhost:6379

# ChromaDB Configuration
CHROMA_DB_PATH=./chroma_db

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=your_super_secret_key_here

# Voice Settings (Optional)
VOICE_ENABLED=true
```

### 3. Database Setup

```bash
# Start PostgreSQL and Redis
# Using Docker:
docker run --name postgres_chatbot -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
docker run --name redis_chatbot -p 6379:6379 -d redis:alpine

# Create database
psql -U postgres -c "CREATE DATABASE chatbot_db;"
```

### 4. Initialize Database Tables

```bash
cd backend
python -m app.core.database.init_db
```

### 5. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
python -m app.main
# Runs on http://localhost:8001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

## Features Implemented

### ✅ Core Features

| Feature | Status | Location |
|---------|--------|----------|
| Multi-Agent Architecture | ✅ | `backend/app/agents/` |
| NLU (Intent/Entity Extraction) | ✅ | `backend/app/agents/nlu/` |
| RAG (Document Q&A) | ✅ | `backend/app/agents/knowledge/` |
| Text-to-SQL | ✅ | `backend/app/agents/sql/` |
| Translation (12 languages) | ✅ | `backend/app/agents/translation/` |
| Voice (STT/TTS) | ✅ | `backend/app/agents/voice/` |
| Design Workflow | ✅ | `backend/app/agents/design/` |
| Analytics | ✅ | `backend/app/agents/analytics/` |
| JWT Authentication | ✅ | `backend/app/core/auth/` |
| WebSocket Chat | ✅ | `backend/app/api/websocket/` |

### ✅ Frontend Features

| Feature | Status | Location |
|---------|--------|----------|
| Chat Interface | ✅ | `frontend/src/components/Chat/` |
| Language Selector | ✅ | `frontend/src/components/Chat/LanguageSelector.tsx` |
| Voice Button | ✅ | `frontend/src/components/Chat/VoiceButton.tsx` |
| Avatar System | ✅ | `frontend/src/components/Chat/Avatar.tsx` |
| Settings Page | ✅ | `frontend/src/pages/SettingsPage.tsx` |
| Analytics Dashboard | ✅ | `frontend/src/pages/AnalyticsDashboard.tsx` |
| Redux Store | ✅ | `frontend/src/store/` |

## API Endpoints

### Chat
- `POST /api/chat/send` - Send message
- `GET /api/chat/history/{session_id}` - Get chat history

### Voice
- `POST /api/voice/transcribe` - Speech-to-text
- `POST /api/voice/synthesize` - Text-to-speech
- `GET /api/voice/voices` - List available voices

### Translation
- `POST /api/translate` - Translate text
- `POST /api/translate/detect` - Detect language
- `GET /api/translate/languages` - Supported languages

### Analytics
- `GET /api/analytics/dashboard` - Analytics overview
- `GET /api/analytics/most-asked` - Popular questions
- `GET /api/analytics/satisfaction` - User satisfaction

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## FRD Requirements Checklist

| FRD Requirement | Status |
|-----------------|--------|
| NLU (Intent/Entities) | ✅ |
| Multilingual Support (12 languages) | ✅ |
| Voice (STT/TTS) | ✅ |
| RAG Document Understanding | ✅ |
| Text-to-SQL | ✅ |
| Guided Design Flow | ✅ |
| User Preferences | ✅ |
| Learning Loop | ✅ |
| Knowledge Gap Detection | ✅ |
| Human Handoff | ✅ |
| Analytics Dashboard | ✅ |
| Explainability | ✅ |
| Privacy (GDPR compliant) | ✅ |
| JWT Authentication | ✅ |

## Project Structure

```
CLIENT-AI-PROJECT/
├── backend/
│   ├── app/
│   │   ├── agents/           # Multi-agent system
│   │   │   ├── nlu/         # Intent classification
│   │   │   ├── knowledge/    # RAG agent
│   │   │   ├── sql/         # Text-to-SQL
│   │   │   ├── translation/  # Multilingual
│   │   │   ├── voice/       # STT/TTS
│   │   │   ├── design/      # Design workflow
│   │   │   ├── feedback/    # User feedback
│   │   │   └── analytics/   # Analytics & learning
│   │   ├── api/             # REST endpoints
│   │   ├── core/            # Auth, config, database
│   │   └── models/          # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/         # Redux store
│   │   └── types/         # TypeScript types
│   └── package.json
└── docker-compose.yml      # Docker services
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env

2. **OpenAI API Error**
   - Verify API key is set
   - Check quota limits

3. **CORS Errors**
   - Frontend runs on port 5173
   - Backend on port 8001
   - Ensure CORS is configured

4. **Redis Connection**
   - Start Redis server
   - Check REDIS_URL

## Next Steps

1. Install dependencies (run pip install and npm install)
2. Configure .env file
3. Start PostgreSQL and Redis
4. Initialize database
5. Run backend: `python -m app.main`
6. Run frontend: `npm run dev`
7. Open http://localhost:5173
