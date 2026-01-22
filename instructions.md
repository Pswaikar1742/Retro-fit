# Retro-Fit: Autonomous Legacy Code Modernization Platform

## 1. Project Vision
**Retro-Fit** is a platform designed to modernize "Zombie Code" (legacy Python 2.7, unmaintained scripts, zip files). It uses a Multi-Agent AI system to autonomously:
1.  **Sanitize:** Remove PII and secrets.
2.  **Refactor:** Upgrade code to modern standards (e.g., Python 3.11).
3.  **Containerize:** Generate valid `Dockerfile` and `requirements.txt`.
4.  **Verify:** Trigger a build in **Google Cloud Build** to ensure validity.
5.  **Self-Heal:** If the build fails, the AI analyzes logs, fixes code, and retries.

## 2. Tech Stack (Google-First)
-   **Frontend:** Next.js 14 (App Router), Tailwind CSS (Dark/Cyberpunk Theme), Lucide React.
-   **Backend:** Python 3.11 (FastAPI) acting as the Orchestrator.
-   **AI Engine:** Google Vertex AI SDK (`gemini-1.5-pro`).
-   **Infrastructure:**
    -   **Google Cloud Storage (GCS):** For storing uploaded ZIPs and build artifacts.
    -   **Google Cloud Build:** For validation and container building.
    -   **Google Cloud Run:** For hosting backend agents and user apps.
    -   **Google Pub/Sub:** For async job queuing.

## 3. The "Golden Pipeline" (Logic Flow)
1.  **Ingest:** User uploads ZIP -> Backend saves to `temp/` (or GCS).
2.  **Audit:** Backend sends code context to Gemini with prompt: "Analyze this architecture."
3.  **Action:** Backend asks Gemini: "Refactor to Python 3 and write a Dockerfile. Output JSON."
4.  **Validation Loop:**
    -   Backend saves files.
    -   Backend triggers `gcloud builds submit`.
    -   **If Build Fails:** Capture logs -> Feed back to Gemini -> Overwrite files -> Retry.
    -   **If Build Succeeds:** Return "Success" URL to Frontend.

## 4. Coding Standards
-   **Python:** 
    -   Use Type Hints (`def func() -> str:`).
    -   Use `pydantic` for structured data extraction from Gemini.
-   **Frontend:** 
    -   Use TypeScript interfaces.
    -   UI Style: "Hacker Console" (Green text, Black background).
-   **Error Handling:** 
    -   Never fail silently.
    -   Catch JSON parse errors from AI and retry.
