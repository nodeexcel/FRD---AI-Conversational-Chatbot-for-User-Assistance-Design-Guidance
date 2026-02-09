@echo off
REM Start Docker services for the AI Chatbot

echo Starting PostgreSQL...
docker run --name postgres_chatbot -e POSTGRES_PASSWORD=chatbot_secret -p 5432:5432 -d postgres

echo Starting Redis...
docker run --name redis_chatbot -p 6379:6379 -d redis:alpine

echo Starting ChromaDB...
docker run --name chromadb_chatbot -p 8000:8000 -d chromadb/chroma:latest

echo.
echo All services started!
echo.
echo PostgreSQL: localhost:5432 (user: postgres, password: chatbot_secret)
echo Redis: localhost:6379
echo ChromaDB: localhost:8000
echo.
echo Now start the backend:
echo cd backend
echo python -m app.main
echo.
echo Then start the frontend:
echo cd frontend
echo npm run dev
