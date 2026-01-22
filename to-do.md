# Retro-Fit Development To-Do List

## Phase 1: Environment & Foundation
- [ ] Configure `backend/app/config.py` for GCP credentials and settings.
- [ ] Set up Google Cloud Project (enable Vertex AI, Cloud Build, Cloud Run, GCS APIs).
- [ ] Create basic `pydantic` models for API requests/responses (`models.py`).

## Phase 2: Core Backend (FastAPI)
- [ ] Implement file upload endpoint (`/upload`) to accept ZIP files.
- [ ] Implement GCS upload logic (upload raw "zombie" code to a bucket).
- [ ] Create `SanitizerService` to strip secrets/PII before processing.

## Phase 3: AI Agents (Vertex AI + Gemini)
- [ ] Implement `VertexAIClient` wrapper for interacting with `gemini-1.5-pro`.
- [ ] Create **Auditor Agent**: Analyzes legacy code structure.
- [ ] Create **Refactor Agent**: Generates modernized Python 3.11 code + Dockerfile.
- [ ] ensure JSON output parsing is robust (handles markdown code blocks from LLM).

## Phase 4: The Build & Validation Loop
- [ ] Implement `CloudBuildService` to trigger `gcloud builds submit` programmatically.
- [ ] Implement **Self-Healing Logic**:
    - [ ] Polling/Webhook for build status.
    - [ ] If fail: Retrieve logs -> Create prompt with logs -> Call Refactor Agent -> Retry.
    - [ ] If success: Mark job as complete.

## Phase 5: Frontend (Next.js/Cyberpunk UI)
- [ ] Update `UploadZone.tsx` to handle file drag-and-drop and progress.
- [ ] Create `ConsoleOutput.tsx` streaming logs (simulated or real-time from backend).
- [ ] Visualize the "Modernization Steps" (Audit -> Refactor -> Verify).
- [ ] details page to view/download converted code.

## Phase 6: Deployment & Polish
- [ ] Dockerize the Retro-Fit Backend for Cloud Run.
- [ ] Dockerize the Frontend.
- [ ] Final end-to-end integration test with `samples/zombie_code`.
