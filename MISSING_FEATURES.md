# 🚨 RETRO-FIT: MISSING FEATURES & ERROR AUDIT REPORT

**Generated**: January 23, 2026  
**Status**: Ready for Implementation  
**Demo Video Duration**: 3 minutes (Target)

---

## 📋 CRITICAL ERRORS FOUND & TO BE FIXED

### **Error #1: Duplicate `/upload` Endpoints** ❌
**Location**: `main.py` + `modernization.py`  
**Issue**: Two separate POST `/upload` endpoints exist
- `main.py:/upload` → Direct Gemini call (synchronous, no sanitization)
- `modernization.py:/upload` → Sanitized flow with GCS upload

**Impact**: FastAPI will only register one (last one wins). Router not included in main.py.

**Fix**: Include router in main.py and remove duplicate endpoint from main.py

---

### **Error #2: main.py Not Using Configured Settings** ❌
**Location**: `main.py` (lines 33-34)
```python
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "retro-fit-hackathon")  # WRONG
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")  # WRONG
```

**Issue**: Using old env var names, not using the `settings` from `config.py`

**Expected**:
```python
from app.core.config import settings
PROJECT_ID = settings.GCP_PROJECT_ID
LOCATION = settings.GCP_REGION
```

**Fix**: Import settings from config.py and use them

---

### **Error #3: Gemini Model Name Outdated** ⚠️
**Location**: `main.py` (line 99)
```python
model_name = "gemini-1.5-pro-preview-0409"  # Preview version, may not exist
```

**Issue**: Using preview model, should use stable version

**Fix**: Change to `settings.VERTEX_AI_MODEL` (defaults to "gemini-1.5-pro")

---

### **Error #4: Typo in modernization.py** 🐛
**Location**: `modernization.py` (line 84)
```python
message="Zombie code received and sanitized. Ready for autopsyt.",  # TYPO: "autopsyt"
```

**Fix**: Change to "autopsy" or "analysis"

---

### **Error #5: Missing Router Integration in main.py** ❌
**Location**: `main.py`

**Issue**: `modernization.py` router exists but is NOT included in main.py

**Fix**: Add this after CORS middleware:
```python
from app.routers import modernization
app.include_router(modernization.router)
```

---

### **Error #6: frontend/page.tsx API Endpoint Mismatch** ⚠️
**Location**: `frontend/src/app/page.tsx` (line 56)
```typescript
const response = await fetch('http://localhost:8000/upload', {
```

**Issue**: Endpoint exists but doesn't match the `ProcessingStateResponse` structure  
**Current response**: Returns structured JSON with status, steps_completed, etc.  
**Frontend expects**: `{ refactored_code, dockerfile }`

**Fix**: Parse the response correctly or change backend to return both

---

### **Error #7: Download Functionality Incomplete** ⚠️
**Location**: `frontend/src/app/page.tsx` (lines ~140)
```typescript
const downloadArtifacts = () => {
    // Only downloads refactored_code
    // Missing: Dockerfile download, JSON export, etc.
}
```

**Fix**: Implement multi-file download (refactored_code.py + Dockerfile)

---

## ❌ MISSING SERVICES/FILES (BLOCKING)

### **1. `backend/app/services/cloudbuild.py`** 🔴 CRITICAL
**Status**: Does NOT exist  
**Purpose**: Trigger Cloud Build, poll status, retrieve logs  
**Requirements**:
- `trigger_build()` - Submit source to Cloud Build
- `get_build_status()` - Poll build status
- `get_build_logs()` - Retrieve build output for self-healing
- `simulate_mode` - Mock responses for hackathon demo (optional)

**Dependencies**:
```python
from google.cloud import build_v1
```

---

### **2. `backend/app/services/vertexai_client.py`** 🔴 CRITICAL
**Status**: Does NOT exist (logic is hardcoded in main.py)  
**Purpose**: Reusable Gemini wrapper with robust JSON parsing  
**Requirements**:
- `VertexAIClient.analyze_code()` - Audit code structure
- `VertexAIClient.refactor_code()` - Generate refactored code + Dockerfile
- `VertexAIClient.fix_code_from_logs()` - Self-healing from build failures
- Robust JSON parsing with markdown code block handling
- Retry logic for API failures

---

### **3. `backend/app/agents/auditor.py`** 🟡 IMPORTANT
**Status**: Does NOT exist  
**Purpose**: Analyze legacy code before refactoring  
**Should return**:
```python
{
    "architecture": "Flask app with SQLite",
    "issues": ["print statements", "Python 2 imports", "unicode errors"],
    "recommendation": "Refactor to FastAPI + PostgreSQL"
}
```

---

### **4. `backend/app/agents/refactor.py`** 🟡 IMPORTANT
**Status**: Does NOT exist (basic logic in main.py)  
**Purpose**: Generate modernized code + Dockerfile  
**Should return**:
```python
{
    "refactored_code": "...",
    "dockerfile": "...",
    "requirements_txt": "..."
}
```

---

### **5. `backend/app/utils/json_parser.py`** 🟡 IMPORTANT
**Status**: Does NOT exist  
**Purpose**: Robust JSON extraction from Gemini responses  
**Should handle**:
- Markdown code blocks (\`\`\`json ... \`\`\`)
- Extra whitespace/newlines
- Partial JSON responses
- Fallback mocking

---

### **6. Self-Healing Pipeline** 🔴 CRITICAL
**Status**: Does NOT exist  
**Location**: Should be in `main.py:/upload` endpoint  
**Logic**:
```
1. User uploads ZIP
2. Sanitize code
3. Call Refactor Agent
4. Trigger Cloud Build
5. Wait for build result
6. If FAIL:
   - Retrieve build logs
   - Create new prompt with logs
   - Call Refactor Agent again
   - Trigger Build again
   - Retry up to 3 times
7. Return result (success/failure)
```

---

### **7. Frontend Log Streaming** 🟡 IMPORTANT
**Status**: Partially done  
**Issue**: Logs are simulated, not real  
**Missing**:
- WebSocket or Server-Sent Events (SSE) for real-time logs
- Integration with backend progress tracking
- Proper log parsing and formatting

---

### **8. Download UI Components** 🟡 IMPORTANT
**Status**: Incomplete  
**Missing**:
- Multi-file download (Dockerfile + Python + requirements.txt)
- Copy-to-clipboard for code
- Code viewer/syntax highlighting
- Details page showing:
  - Original architecture analysis
  - Issues found
  - Refactoring strategy
  - Generated Dockerfile preview

---

## 📦 MISSING ENDPOINTS & FEATURES

### **Backend Endpoints Missing**

| Endpoint | Method | Status | Purpose |
|----------|--------|--------|---------|
| `/api/analyze/{submission_id}` | GET | ❌ | Retrieve analysis results |
| `/api/status/{submission_id}` | GET | ❌ | Check modernization progress |
| `/api/download/{submission_id}` | GET | ❌ | Download refactored code |
| `/api/logs/{submission_id}` | GET | ❌ | Retrieve build logs |
| `/api/health` | GET | ⚠️ | Exists but incomplete |

---

## 🎬 3-MINUTE DEMO FLOW

For an impressive 3-minute demo, you need:

1. **0:00-0:30** - Show the cyberpunk UI
   - Dark hacker console aesthetic
   - File drag-drop animation
   - Status indicators

2. **0:30-1:30** - Upload & Process
   - Upload `samples/zombie_code/app.py` (wrap in ZIP)
   - Show real-time logging
   - Display sanitization steps
   - Show Gemini refactoring

3. **1:30-2:30** - Cloud Build Verification (THE KILLER FEATURE)
   - Show build triggered in GCP
   - Display build logs streaming
   - Demonstrate self-healing if build fails
   - Show final success

4. **2:30-3:00** - Download & Results
   - Download refactored code
   - Show Dockerfile
   - Quick side-by-side comparison (before/after)
   - "Deploy to Cloud Run" CTA

---

## ✅ CURRENT STATUS SUMMARY

| Component | Status | Priority | ETA |
|-----------|--------|----------|-----|
| Config & Settings | ✅ Done | — | — |
| Storage Service (GCS) | ✅ Done | — | — |
| Sanitizer Service | ✅ Done | — | — |
| Upload Endpoint | ⚠️ Partial | 🔴 CRITICAL | 15 min |
| Vertex AI Client | ❌ Missing | 🔴 CRITICAL | 30 min |
| Cloud Build Service | ❌ Missing | 🔴 CRITICAL | 45 min |
| Self-Healing Loop | ❌ Missing | 🔴 CRITICAL | 1 hour |
| Frontend UI | ⚠️ Partial | 🟡 Important | 30 min |
| Demo Video Ready | ❌ No | 🟡 Important | 30 min |

---

## 🎯 RECOMMENDED IMPLEMENTATION ORDER

### **ROUND 1: Fix Errors (15 minutes)**
1. Fix duplicate `/upload` endpoints
2. Update main.py to use settings from config.py
3. Include router in main.py
4. Fix typo in modernization.py

### **ROUND 2: Build Critical Services (1 hour)**
1. Create `vertexai_client.py` (Gemini wrapper)
2. Create `cloudbuild.py` (Cloud Build integration)
3. Create `json_parser.py` (robust JSON extraction)
4. Implement agents (auditor.py, refactor.py)

### **ROUND 3: Implement Self-Healing (45 minutes)**
1. Update `/upload` endpoint with retry logic
2. Add state persistence (track submission_id progress)
3. Implement build status polling
4. Add log retrieval and feedback loop

### **ROUND 4: Polish Frontend (30 minutes)**
1. Fix response parsing to match backend
2. Implement real-time log streaming
3. Add multi-file download
4. Add code viewer component

### **ROUND 5: Demo Ready (15 minutes)**
1. Test end-to-end with sample zombie code
2. Prepare demo script
3. Create demo video

---

## 📋 DETAILED FIX CHECKLIST

- [ ] Fix duplicate `/upload` endpoints
- [ ] Update main.py Vertex AI initialization
- [ ] Include modernization router in main.py
- [ ] Fix typo "autopsyt" → "autopsy"
- [ ] Create vertexai_client.py
- [ ] Create cloudbuild.py
- [ ] Create json_parser.py utility
- [ ] Create auditor.py agent
- [ ] Create refactor.py agent
- [ ] Implement self-healing loop
- [ ] Fix frontend response parsing
- [ ] Add real-time log streaming
- [ ] Implement multi-file download
- [ ] Test with zombie_code sample
- [ ] Create demo video script

