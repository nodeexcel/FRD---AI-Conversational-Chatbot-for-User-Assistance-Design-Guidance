# PostgreSQL Setup Guide for Windows

## Option 1: Using Docker (Recommended)

This is the easiest method since Docker handles everything.

### Step 1: Install Docker Desktop
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer
4. Verify installation:
   ```cmd
   docker --version
   docker-compose --version
   ```

### Step 2: Configure PostgreSQL in .env file
Edit the `.env` file in your project root:
```env
POSTGRES_USER=chatbot
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=chatbot_db
```

### Step 3: Start PostgreSQL via Docker
```cmd
docker-compose up -d postgres
```

### Step 4: Verify PostgreSQL is Running
```cmd
docker ps
```
You should see `chatbot_postgres` running on port `5432`.

### Step 5: Initialize Database
```cmd
docker exec -i chatbot_postgres psql -U chatbot -d chatbot_db < backend/init-scripts/01-init.sql
```

### Step 6: Connect to PostgreSQL (Optional - for verification)
```cmd
docker exec -it chatbot_postgres psql -U chatbot -d chatbot_db
```

---

## Option 2: Direct PostgreSQL Installation

### Step 1: Download PostgreSQL
1. Go to: https://www.postgresql.org/download/windows/
2. Download PostgreSQL 15 or 16 (Installer)
3. Run the installer

### Step 2: Installation Wizard
1. **Welcome** - Click Next
2. **Installation Directory** - Keep default, click Next
3. **Select Components** - Keep all selected, click Next
4. **Data Directory** - Keep default, click Next
5. **Password** - Enter a strong password, remember it!
   - Set: `your_secure_password`
6. **Port** - Keep default `5432`, click Next
7. **Locale** - Keep default, click Next
8. **Pre Installation Summary** - Click Next
9. **Ready to Install** - Click Install
10. **Completing Setup** - Uncheck "Launch Stack Builder", click Finish

### Step 3: Configure pgAdmin (Optional)
1. Open pgAdmin from Start Menu
2. Set a master password
3. Right-click "Servers" → "Create" → "Server"
4. **General tab**: Name: `Chatbot DB`
5. **Connection tab**:
   - Host: `localhost`
   - Port: `5432`
   - Username: `postgres`
   - Password: `your_secure_password`
6. Click Save

### Step 4: Create Database and User
1. In pgAdmin, expand your server
2. Right-click "Databases" → "Create" → "Database"
3. Database name: `chatbot_db`
4. Click Save

5. Open Query Tool (Tools → Query Tool)
6. Run:
```sql
-- Create user
CREATE USER chatbot WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot;

-- Connect to database
\c chatbot_db

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO chatbot;
```

### Step 5: Initialize Database Schema
Run the SQL script in pgAdmin:
1. Open `backend/init-scripts/01-init.sql`
2. Copy all content
3. Paste in Query Tool and run (F5)

---

## Connecting Your Backend to PostgreSQL

### Step 1: Update .env file
```env
# If using Docker:
DATABASE_URL=postgresql+asyncpg://chatbot:your_secure_password@localhost:5432/chatbot_db

# If using local installation:
DATABASE_URL=postgresql+asyncpg://chatbot:your_secure_password@localhost:5432/chatbot_db
```

### Step 2: Test Connection
Start your backend:
```cmd
cd backend
uvicorn app.main:app --reload
```

If connected successfully, you'll see:
```
INFO:     Database connection: healthy
```

---

## Common PostgreSQL Commands

### Connect via Command Line
```cmd
psql -U chatbot -d chatbot_db
```

### List Databases
```sql
\l
```

### List Tables
```sql
\dt
```

### Describe Table
```sql
\d products
```

### Exit psql
```sql
\q
```

---

## Troubleshooting

### "Connection refused" Error
- Make sure PostgreSQL service is running
- Check port (default 5432)
- Verify firewall settings

### "Role does not exist" Error
- Check username/password in .env
- Ensure user was created

### "Database does not exist" Error
- Create the database first
- Check spelling of database name

### Reset Database
```sql
-- Drop all tables (be careful!)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Re-run init script
\i backend/init-scripts/01-init.sql
```

---

## Docker PostgreSQL Management

### Start PostgreSQL
```cmd
docker-compose up -d postgres
```

### Stop PostgreSQL
```cmd
docker-compose stop postgres
```

### Restart PostgreSQL
```cmd
docker-compose restart postgres
```

### View Logs
```cmd
docker-compose logs postgres
```

### Remove PostgreSQL Data
```cmd
docker-compose down -v
docker-compose up -d postgres
```

---

## PostgreSQL GUI Tools (Optional)

### pgAdmin 4
- Download: https://www.pgadmin.org/download/
- Web-based interface

### DBeaver
- Download: https://dbeaver.io/download/
- Universal database tool

### HeidiSQL
- Download: https://www.heidisql.com/download.php
- Lightweight Windows tool

### DataGrip
- JetBrains IDE
- Paid but powerful
