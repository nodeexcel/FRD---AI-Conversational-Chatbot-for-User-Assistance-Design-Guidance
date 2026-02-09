# Docker Desktop Not Running - Fix Guide

## The Error:
```
unable to get image 'redis:7-alpine': error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/images/redis:7-alpine/json": open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**This means Docker Desktop is NOT running!**

---

## FIX: Start Docker Desktop

### Method 1: Start from Windows Menu
1. Click **Windows Start Menu**
2. Type: **"Docker Desktop"**
3. **Click Docker Desktop** to open it
4. **Wait 2-3 minutes** for Docker to fully start
5. You'll see "Docker Desktop is running" in bottom-right corner

### Method 2: Command Line
```bash
# Run as Administrator
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

---

## After Docker is Running:

```bash
cd "c:\Users\PRATEEK SARASWAT\OneDrive\Desktop\Excellence Technologies\CLIENT-AI-PROJECT"
docker-compose up -d
```

---

## Verify Docker is Working:

```bash
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE      COMMAND   CREATED   STATUS   PORTS     NAMES
```

If you see containers listed, Docker is working!

---

## If Docker Still Doesn't Work:

### Restart Docker Desktop:
1. Right-click Docker icon in system tray (bottom-right)
2. Click **"Restart"**
3. Wait for restart
4. Run `docker-compose up -d` again

### Check Docker Service:
```bash
docker version
```

Should show:
```
Client: Docker Desktop
Version: 25.x.x
Server: Docker Desktop
Version: 25.x.x
```

---

## Quick Test Commands:

```bash
# Test Docker
docker run hello-world

# Test Docker Compose
docker-compose --version
```

---

## Still Having Issues?

1. **Restart your computer**
2. **Reinstall Docker Desktop** from https://docker.com
3. Make sure **WSL 2** is installed (required for Docker on Windows)
