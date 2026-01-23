# 🎯 RETRO-FIT DEMO VIDEO PRODUCTION PLAN

**Target**: 3-Minute Demonstration Video  
**Date**: January 23, 2026  
**Status**: Code audit complete, ready for implementation

---

## 🎬 DEMO VIDEO SCRIPT (3 Minutes)

### **SEGMENT 1: Intro & UI (0:00-0:30)**

**Visual**: Show cyberpunk UI at localhost:3000
```
Scene 1 (5 sec):
- Camera pan across dark terminal-style interface
- Show RETRO-FIT logo glowing in green
- Display "AUTONOMOUS LEGACY CODE MODERNIZATION PLATFORM"

Scene 2 (10 sec):
- Highlight drag-and-drop zone
- Show file icon with "DROP ZOMBIE CODE HERE"
- Display status indicators (INGESTION | AI REFACTOR | BUILD VERIFY)

Scene 3 (15 sec):
- Show the hacker terminal aesthetic
- Green text on black background
- Monospace font with glowing effects
- "SYSTEM: ONLINE" and "VERTEX AI: CONNECTED" status
```

**Talking Points**:
- "This is Retro-Fit, an autonomous legacy code modernization platform"
- "Built with Next.js frontend, FastAPI backend, and Google Vertex AI"
- "Notice the cyberpunk hacker console aesthetic - fully immersive"

---

### **SEGMENT 2: Upload & Processing (0:30-1:30)**

**Visual**: Upload zombie code and watch real-time processing

```
Scene 1 (10 sec):
- Drag ZIP file into upload zone
- Show animation: "UPLOADING..."
- File icon appears with "sample_zombie_code.zip"

Scene 2 (20 sec):
- Terminal logs start appearing in real-time:
  [12:34:56] > File loaded: sample_zombie_code.zip
  [12:34:57] > Initiating secure upload...
  [12:34:58] > Sending to Backend Orchestrator...
  [12:34:59] > Upload complete. Vertex AI Agent initiated.
  [12:35:00] > Analyzing Legacy Code Architecture...
  [12:35:02] > Refactoring to Python 3.11...
  [12:35:05] > Generating Container Configuration...

Scene 3 (10 sec):
- Show status boxes updating:
  INGESTION: ✓ (Green with glow)
  AI REFACTOR: ⟳ (Spinning yellow)
  BUILD VERIFY: ○ (Waiting, gray)

Scene 4 (10 sec):
- Refactored code appears in terminal output
- Show preview: "FROM python:3.11-slim"
- Display Dockerfile snippet
```

**Talking Points**:
- "User drops a ZIP file of legacy Python 2 code"
- "The system extracts and sanitizes sensitive data - API keys, credentials, secrets are removed"
- "Gemini AI analyzes the code structure and immediately refactors to Python 3.11"
- "Look at the real-time logs - each step is tracked and visible"

---

### **SEGMENT 3: Cloud Build Verification (1:30-2:30)**

**Visual**: THE KILLER FEATURE - Verify it actually builds

```
Scene 1 (15 sec):
- Status updates: AI REFACTOR ✓ → BUILD VERIFY ⟳
- New terminal output:
  [12:35:10] > Refactoring Complete. Triggering Cloud Build...
  [12:35:11] > Submitting to Google Cloud Build...
  [12:35:15] > Build ID: abc123xyz456
  [12:35:20] > Build logs:
    Step 1/5: FROM python:3.11-slim
    Step 2/5: COPY requirements.txt .
    Step 3/5: RUN pip install -r requirements.txt
    Step 4/5: COPY . /app
    Step 5/5: CMD ["python", "app.py"]
    Successfully built image

Scene 2 (15 sec - OPTIONAL: Self-Healing Demo):
- Simulate a build failure:
  [12:36:00] > Build FAILED: ModuleNotFoundError: No module named 'sqlite3'
  [12:36:02] > Retrieving build logs...
  [12:36:05] > Feeding error back to Gemini...
  [12:36:10] > Refactoring code to fix error...
  [12:36:15] > Triggering build retry...
  [12:36:20] > Build SUCCEEDED ✓

Scene 3 (10 sec):
- Status updates: BUILD VERIFY ✓ (Green glow)
- All three status boxes now green and glowing
```

**Talking Points** (without self-healing):
- "Here's the Killer Feature - we don't just generate code"
- "We actually trigger a real Cloud Build to verify it works"
- "The Dockerfile we generated is valid and builds successfully"
- "This proves the code is production-ready, not just generated text"

**Talking Points** (with self-healing demo):
- "What if the build fails? Watch the self-healing in action"
- "Gemini reads the build error logs"
- "It analyzes what went wrong and fixes it automatically"
- "Retry - and it succeeds! The AI learns from its mistakes"

---

### **SEGMENT 4: Download & Results (2:30-3:00)**

**Visual**: Download artifacts and show the transformation

```
Scene 1 (10 sec):
- Show "DOWNLOAD ARTIFACTS" button highlighted
- Click button
- Show file download notification:
  "modernized_app.py"
  "Dockerfile"

Scene 2 (10 sec):
- Open downloaded files in VS Code (split view):
  LEFT: Original Python 2.7 code (with 'print' statements, urllib2)
  RIGHT: Refactored Python 3.11 code (with proper imports, type hints)
  
  Show side-by-side comparison:
  ```
  # BEFORE:
  print 'Hello World'
  import urllib2
  
  # AFTER:
  print('Hello World')
  import urllib.request
  ```

Scene 3 (5 sec):
- Show final status:
  ✓ INGESTION COMPLETE
  ✓ AI REFACTOR COMPLETE
  ✓ BUILD VERIFICATION PASSED
  "Code is production-ready and deployable"
```

**Talking Points**:
- "The refactored code is immediately available for download"
- "All artifacts are generated: modernized Python code, Dockerfile, requirements.txt"
- "This transformation that would take a team days, Retro-Fit handles in minutes"
- "The code is not just generated—it's verified to build and run"

---

## 📋 DEMO CHECKLIST

Before recording video:

### **Code Readiness**
- [ ] All 7 errors fixed
- [ ] Router properly integrated in main.py
- [ ] `vertexai_client.py` created and tested
- [ ] `cloudbuild.py` created (with simulate mode)
- [ ] Self-healing loop implemented
- [ ] Frontend properly parses responses
- [ ] Download functionality works

### **GCP Setup**
- [ ] credentials.json in backend/ (not committed)
- [ ] All APIs enabled (Storage, Build, Vertex AI, Run)
- [ ] GCS bucket accessible
- [ ] Cloud Build can be triggered
- [ ] Vertex AI Gemini responds correctly

### **Sample Data**
- [ ] `samples/zombie_code/app.py` packaged as ZIP
- [ ] Test upload works locally
- [ ] Sanitizer properly strips secrets
- [ ] Gemini returns valid JSON
- [ ] Cloud Build succeeds

### **UI/UX Polish**
- [ ] Dark theme applied correctly
- [ ] Green glow effects visible
- [ ] Console logs are readable
- [ ] Status indicators animate smoothly
- [ ] Download button is functional
- [ ] No console errors in browser

### **Video Recording**
- [ ] Good lighting (dark room recommended for hacker aesthetic)
- [ ] Clear audio (explain each step)
- [ ] Smooth zoom/pan effects
- [ ] Good internet (Cloud Build calls must succeed)
- [ ] Backup: Have simulate mode ready in case GCP is slow

---

## 🎯 KEY TALKING POINTS FOR DEMO

1. **The Problem**: 
   - "Companies are stuck with millions of lines of Python 2 code"
   - "Manual modernization is expensive, time-consuming, error-prone"

2. **The Solution**:
   - "Retro-Fit uses agentic AI to automate the entire process"
   - "From extraction to sanitization to refactoring to verification"

3. **The Killer Feature**:
   - "We don't just generate code—we verify it builds"
   - "If it fails, the AI reads the errors and fixes itself"
   - "Self-healing: The AI learns from build failures"

4. **The Tech Stack**:
   - "Google Vertex AI (Gemini) for code analysis"
   - "Cloud Build for real verification"
   - "Cloud Storage for artifact management"
   - "Modern UI: Next.js + Tailwind in cyberpunk aesthetic"

5. **The Value**:
   - "What took weeks, now takes minutes"
   - "Code quality: Generated and verified by AI"
   - "Ready for production: Dockerized and tested"

---

## ⏱️ TIMING BREAKDOWN

| Segment | Duration | Content |
|---------|----------|---------|
| Intro & UI | 0:30 | Show the cyberpunk interface |
| Upload & Process | 1:00 | Watch real-time refactoring |
| Cloud Build (verify) | 1:00 | Show build success (± self-healing) |
| Download & Results | 0:30 | Download and compare code |
| **Total** | **3:00** | Complete demonstration |

---

## 🚀 IMPLEMENTATION PRIORITY

To get to demo-ready state, implement in this order:

### **CRITICAL (Block Demo Without These)**
1. Fix 7 identified code errors (15 min)
2. Create `vertexai_client.py` (30 min)
3. Create `cloudbuild.py` with simulate mode (45 min)
4. Implement self-healing loop (1 hour)
5. Fix frontend response parsing (20 min)

### **IMPORTANT (Enhances Demo)**
6. Implement log streaming (30 min)
7. Add multi-file download (15 min)
8. Polish error messages (10 min)

### **NICE-TO-HAVE (If Time)**
9. Add code viewer with syntax highlighting
10. Create detailed analysis page
11. Add deployment to Cloud Run button

---

## 📱 DEMO SCRIPT (NARRATOR)

```
[0:00] "This is Retro-Fit, an autonomous legacy code modernization platform."

[0:10] "Legacy code—especially Python 2.7—is a major problem. Companies 
        have millions of lines they need to modernize but can't afford to 
        stop operations."

[0:20] "Retro-Fit solves this with agentic AI. Watch what happens when 
        I upload some zombie code."

[0:35] "I'll drag and drop a ZIP file of Python 2.7 code here."

[0:45] "The system extracts it, sanitizes away any secrets or credentials,
        and sends it to Google Vertex AI for analysis."

[1:05] "Gemini is refactoring the code to Python 3.11 in real-time.
        Watch the logs as each step completes."

[1:25] "Now for the killer feature. We don't just generate code—we verify 
        it actually builds. Retro-Fit is submitting to Google Cloud Build."

[1:40] "The Dockerfile we generated is being tested. And... success! 
        The build passed."

[1:55] "This proves the code is production-ready, not just generated text."

[2:10] "Here's the refactored code, ready to download. From Python 2.7 
        print statements to modern 3.11 syntax."

[2:30] "All the artifacts are ready: refactored code, Dockerfile, 
        requirements.txt."

[2:45] "What would take a team days, Retro-Fit handles in minutes.
        And it's verified to build and run on Google Cloud."

[3:00] "Retro-Fit: The future of legacy code modernization."
```

---

## 📹 VIDEO PRODUCTION NOTES

- **Format**: 1920x1080 (Full HD)
- **Frame Rate**: 30 fps
- **Audio**: Clear voice-over, ~120 wpm
- **Background Music**: Optional (low-key electronic/tech theme)
- **Subtitles**: Recommended (technical content)
- **File Size**: < 100 MB (for easy sharing)

---

**Status**: Ready for Implementation  
**Next Step**: Execute fixes in order and record demo  
**Estimated Time**: 4 hours (fixes + video)

