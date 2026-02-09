# AI Conversational Chatbot - Complete Project

## Overview
This is a multi-agent AI Conversational Chatbot for User Assistance & Design Guidance.

## Tech Stack
- **Frontend**: React.js with TypeScript
- **Backend**: Python with FastAPI
- **LLM**: LLaMA (Open Source)
- **NLU**: Rasa / Custom
- **RAG**: LangChain + Vector DB
- **Database**: PostgreSQL + Redis + Vector DB
- **Voice**: Whisper (STT) + Coqui TTS

## Project Structure

```
├── frontend/                 # React.js frontend application
├── backend/                  # Python FastAPI backend
├── docker-compose.yml        # Docker Compose configuration
├── .env.example             # Environment variables template
├── README.md                # Project documentation
└── docs/                    # Documentation
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose up -d` for services
4. Start backend: `cd backend && uvicorn app.main:app --reload`
5. Start frontend: `cd frontend && npm install && npm start`

## Features
- Conversational AI with LLaMA
- Multi-agent architecture (NLU, Design, Knowledge, SQL, Voice, Translation)
- RAG-based knowledge retrieval
- Voice input/output (STT/TTS)
- Multilingual support
- Design assistance workflow
- Continuous learning from feedback

## License
Proprietary - Excellence Technologies
