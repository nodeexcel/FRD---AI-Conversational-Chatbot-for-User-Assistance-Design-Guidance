# AI Conversational Chatbot - Setup Guide

## Prerequisites

Before running this project, you need to have the following installed:

### 1. System Requirements
- **Operating System**: Windows 11, macOS, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: Minimum 20GB free space
- **CPU**: Multi-core processor (4+ cores recommended)

### 2. Required Software

#### A. Docker & Docker Compose
**Windows/macOS:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install and restart your computer
3. Verify installation:
```bash
docker --version
docker-compose --version
```

**Linux (Ubuntu):**
```bash
# Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

#### B. Node.js (v18+)
**Windows/macOS:**
1. Download from https://nodejs.org (LTS version)
2. Install Node.js
3. Verify:
```bash
node --version
npm --version
```

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### C. Python (3.11+)
**Windows/macOS:**
1. Download from https://www.python.org/downloads/
2. Install Python (check "Add Python to PATH")

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip
```

#### D. Git
**All Platforms:**
```bash
git --version
```

---

## Step-by-Step Setup

### Step 1: Clone the Repository

```bash
# Navigate to your projects directory
cd /path/to/your/projects

# Clone the repository
git clone <repository-url>
cd CLIENT-AI-PROJECT
```

### Step 2: Configure Environment Variables

```bash
# Copy environment templates
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

**Edit `.env` file:**
```env
# Database
POSTGRES_USER=chatbot
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=chatbot_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database (Weaviate)
WEAVIATE_URL=http://localhost:8080

# MongoDB
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=secure_password_here

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=secure_password_here

# LLM Configuration (optional - uses mock by default)
LLAMA_MODEL_PATH=/models/llama-2-7b-chat.gguf

# Application
DEBUG=true
LOG_LEVEL=INFO
```

### Step 3: Start Infrastructure Services (Docker)

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

**Expected Running Services:**
| Service | Port | URL |
|---------|------|-----|
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Weaviate | 8080 | localhost:8080 |
| Elasticsearch | 9200 | localhost:9200 |
| MongoDB | 27017 | localhost:27017 |
| MinIO | 9000, 9001 | localhost:9000 |

### Step 4: Initialize Database

```bash
# Wait for PostgreSQL to be ready, then run init script
docker exec -i chatbot_postgres psql -U chatbot -d chatbot_db < backend/init-scripts/01-init.sql
```

### Step 5: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Backend should be running at: http://localhost:8000
# API docs: http://localhost:8000/api/docs
```

### Step 6: Setup Frontend

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend should be running at: http://localhost:3000
```

---

## Optional: Install ML Models

### LLaMA Model (for local LLM)
```bash
# Download LLaMA 2 7B Chat model
# Using huggingface-hub
pip install huggingface-hub
python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='TheBloke/Llama-2-7B-Chat-GGUF',
    filename='llama-2-7b-chat.Q4_K_M.gguf',
    local_dir='/models/llama-2-7b-chat.gguf'
)
"
```

### Whisper Model (for STT)
```bash
# Whisper models are downloaded automatically on first use
# Models available: tiny, base, small, medium, large
```

---

## Verification Checklist

- [ ] Docker services running (postgres, redis, weaviate, mongodb)
- [ ] Backend API accessible at http://localhost:8000
- [ ] API docs visible at http://localhost:8000/api/docs
- [ ] Frontend accessible at http://localhost:3000
- [ ] Health check returns healthy status
- [ ] Chat messages can be sent and received

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000
# macOS/Linux:
lsof -i :8000

# Kill the process or change port in .env
```

### Docker Issues
```bash
# Restart Docker daemon
# Windows/macOS: Restart Docker Desktop
# Linux:
sudo systemctl restart docker

# Clear Docker cache and rebuild
docker-compose down
docker system prune -a
docker-compose up -d
```

### Python Virtual Environment Issues
```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Node_modules Issues
```bash
# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Development Workflow

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting
```bash
# Backend (Black, isort)
cd backend
black .
isort .

# Frontend (Prettier)
cd frontend
npx prettier --write .
```

### Adding New Dependencies
```bash
# Backend
cd backend
pip install <package>
pip freeze > requirements.txt

# Frontend
cd frontend
npm install <package>
```

---

## Production Deployment

For production deployment, see:
- Kubernetes deployment manifests
- Docker production builds
- CI/CD pipeline setup
