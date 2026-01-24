# 🚀 QUICK START GUIDE

## 5-Minute Local Setup

### Prerequisites
```bash
python 3.11+
docker & docker-compose
node 18+
```

### 1. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Run with Docker Compose
```bash
docker-compose up
```

Visit: http://localhost:3000

### 3. Test the Pipeline
```bash
# Create a test ZIP with Python file
cd samples/zombie_code
zip -r test.zip app.py
```

Upload `test.zip` to http://localhost:3000

---

## 📊 What Happens When You Upload

```
┌─────────────────────────────────────────┐
│ 1. INGEST & SANITIZE                    │
│ ✓ Receive ZIP                           │
│ ✓ Extract files                         │
│ ✓ Remove secrets (10+ patterns)         │
│ ✓ Find main Python file                 │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. AUDIT (CodeAuditor)                  │
│ ✓ Analyze code structure                │
│ ✓ Identify legacy patterns              │
│ ✓ Return: issues, difficulty, time est. │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. REFACTOR (CodeRefactorer)            │
│ ✓ Generate Python 3.11 code             │
│ ✓ Add type hints, async/await           │
│ ✓ Create Dockerfile                     │
│ ✓ Generate requirements.txt             │
└─────────────────────────────────────────┘
              ↓ (max 3 retries)
┌─────────────────────────────────────────┐
│ 4. VERIFY BUILD (CloudBuildService)     │
│ ✓ Trigger Cloud Build                   │
│ ✓ Poll status                           │
│ ✓ Extract logs on failure               │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. RETURN RESULTS                       │
│ ✓ Refactored Python code                │
│ ✓ Dockerfile                            │
│ ✓ requirements.txt                      │
│ ✓ Analysis metadata                     │
└─────────────────────────────────────────┘
```

---

## 🔑 Key Files

### Backend
- `main.py` - FastAPI app + router setup
- `routers/modernization.py` - /upload endpoint with full pipeline
- `services/auditor.py` - Code analysis
- `services/refactor.py` - Code refactoring
- `services/cloudbuild.py` - Build verification
- `services/vertexai_client.py` - Gemini wrapper
- `utils/json_parser.py` - Response parsing
- `utils/sanitizer.py` - Secret removal

### Frontend
- `page.tsx` - Main UI with drag-drop
- `ConsoleOutput.tsx` - Terminal logs
- `StatusIndicator.tsx` - Pipeline status
- `UploadZone.tsx` - Drag-drop zone

### Config
- `core/config.py` - Pydantic settings
- `docker-compose.yml` - Local dev environment
- `requirements.txt` - Python dependencies

---

## 🧪 Testing

### Unit Tests
```bash
cd backend
python -m pytest app/ -v
```

### Import Validation
```bash
cd /mnt/Data/Techsprint/Retro-fit
python test_imports.py
```

### Manual Testing
1. Upload `samples/zombie_code/app.py` as ZIP
2. Check console logs for pipeline stages
3. Download artifacts when complete

---

## 📝 API Reference

### POST /upload
**Description:** Upload and modernize code

**Request:**
```
Content-Type: multipart/form-data
file: <ZIP archive with Python files>
```

**Response:**
```json
{
  "submission_id": "uuid",
  "status": "COMPLETED",
  "message": "...",
  "steps_completed": ["ingest", "sanitize", "audit", "refactor", "build_triggered"],
  "current_step": "completed",
  "metadata": {
    "issues_found": 5,
    "changes_made": 8,
    "new_features": 3,
    "refactor_iterations": 1,
    "build_id": "abc123",
    "refactored_code": "...",
    "dockerfile": "..."
  }
}
```

### GET /health
**Description:** Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-23T12:00:00Z"
}
```

---

## 🔐 Environment Setup

### Create Credentials File
```bash
# Get service account JSON from GCP Console
# Download credentials.json

mkdir -p backend/secrets
mv credentials.json backend/secrets/

# Export for local testing
export GOOGLE_APPLICATION_CREDENTIALS="backend/secrets/credentials.json"
```

### .env Variables
```bash
GCP_PROJECT_ID=retro-fit-dev-485215
GCP_STORAGE_BUCKET=retro-fit-dev-485215-uploads
VERTEX_AI_MODEL=gemini-1.5-pro
VERTEX_AI_TEMPERATURE=0.3
LOG_LEVEL=INFO
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | `pip install -r requirements.txt` |
| GCS connection error | Check credentials.json path and GOOGLE_APPLICATION_CREDENTIALS |
| Gemini API error | Enable Vertex AI API in GCP Console |
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| Port 3000 in use | `lsof -i :3000` then `kill -9 <PID>` |
| Docker build fails | `docker system prune` then rebuild |

---

## 📦 Deployment Checklist

- [ ] Install dependencies
- [ ] Set GOOGLE_APPLICATION_CREDENTIALS
- [ ] Create GCS bucket
- [ ] Enable Vertex AI API
- [ ] Create Cloud Build
- [ ] Run docker-compose up
- [ ] Visit http://localhost:3000
- [ ] Upload test ZIP
- [ ] Verify pipeline completes
- [ ] Download artifacts

---

## 🎬 3-Minute Demo Script

**1. Show Code** (30 sec)
```
"This is legacy Python 2.x code with issues:
- No type hints
- Synchronous I/O
- Outdated imports"
```

**2. Upload** (10 sec)
- Drag-drop app.py to UI
- Watch pipeline start

**3. Watch Pipeline** (2 min)
- Show console logs updating
- See: Sanitizing → Auditing → Refactoring → Building

**4. Download Results** (10 sec)
- Click "Download Artifacts"
- Show app.py, Dockerfile, requirements.txt

**5. Deploy** (10 sec)
- Run: `docker build -t app . && docker run -p 8000:8000 app`
- Show it running

---

## 📊 Architecture Overview

```
┌──────────────────────────────────────────────────┐
│              FRONTEND (Next.js)                  │
│  ┌─────────────────────────────────────────────┐ │
│  │ Upload Zone | Console Output | Download    │ │
│  └──────────────┬──────────────────────────────┘ │
└─────────────────┼──────────────────────────────────┘
                  │ HTTP
┌─────────────────▼──────────────────────────────────┐
│             BACKEND (FastAPI)                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ /upload endpoint (Self-Healing Pipeline)     │  │
│  │                                              │  │
│  │ → Sanitizer (remove secrets)                │  │
│  │ → CodeAuditor (analyze)                     │  │
│  │ → CodeRefactorer (modernize)                │  │
│  │ → CloudBuildService (verify)                │  │
│  │ → VertexAIClient (Gemini calls)             │  │
│  │ → JSONParser (response handling)            │  │
│  └──────────────────────────────────────────────┘  │
└────────┬─────────────────────────────────────┬─────┘
         │ Storage                             │ AI
         ▼                                     ▼
    ┌────────────┐                    ┌──────────────┐
    │ GCS Bucket │                    │ Vertex AI    │
    │ (uploads)  │                    │ (Gemini)     │
    └────────────┘                    └──────────────┘
```

---

## 📚 Documentation Links

- [FINAL_STATUS.md](FINAL_STATUS.md) - Complete status report
- [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) - Original audit
- [CREDENTIALS_SETUP.md](docs/CREDENTIALS_SETUP.md) - GCP guide
- [DEMO_VIDEO_PLAN.md](docs/DEMO_VIDEO_PLAN.md) - Demo script
- [DOCUMENTATION.md](docs/DOCUMENTATION.md) - Technical docs

---

**Last Updated:** January 23, 2026  
**Status:** ✅ Ready for Demo & Production
