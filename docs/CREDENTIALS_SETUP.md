# 🔐 RETRO-FIT CREDENTIALS & CONFIGURATION GUIDE

**⚠️ SENSITIVE**: This file contains references to credentials. Never commit actual keys to Git.

---

## 📍 GCP CREDENTIALS SETUP

### **Step 1: Locate Your credentials.json**

Your GCP Service Account key should be saved at:
```
backend/credentials.json
```

This file is **IGNORED** by Git (see `.gitignore`), so it's safe to place here.

---

### **Step 2: Verify Service Account Permissions**

Your service account must have these roles:
- ✅ **Editor** (for development)
- Or specifically:
  - `roles/storage.admin` (Cloud Storage access)
  - `roles/cloudbuild.admin` (Cloud Build access)
  - `roles/aiplatform.user` (Vertex AI access)

---

### **Step 3: Set Environment Variables**

When running locally or in Docker, ensure these are set:

```bash
# GCP Project Configuration
export GCP_PROJECT_ID="retro-fit-dev-485215"
export GCP_REGION="us-central1"
export GCP_STORAGE_BUCKET="retro-fit-dev-485215-uploads"
export GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json"

# Vertex AI Configuration
export VERTEX_AI_MODEL="gemini-1.5-pro"
export VERTEX_AI_TEMPERATURE="0.2"

# Logging
export LOG_LEVEL="INFO"
```

**Docker Compose Already Sets These** ✅  
(See `docker-compose.yml` - no additional setup needed)

---

## 🔑 CREDENTIALS.JSON STRUCTURE

Your `credentials.json` should look like this (example):

```json
{
  "type": "service_account",
  "project_id": "retro-fit-dev-485215",
  "private_key_id": "key_id_here",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n",
  "client_email": "retro-fit-service@retro-fit-dev-485215.iam.gserviceaccount.com",
  "client_id": "1234567890",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/retro-fit-service%40retro-fit-dev-485215.iam.gserviceaccount.com"
}
```

**Location**: `backend/credentials.json`

---

## 🪣 GCS BUCKET SETUP

### **Your Current Bucket**
```
gs://retro-fit-dev-485215-uploads/
```

### **Bucket Structure** (Auto-Created)
```
retro-fit-dev-485215-uploads/
├── uploads/
│   └── {submission_id}/
│       ├── source.zip           (Sanitized input code)
│       ├── refactored.py        (Modernized code)
│       ├── Dockerfile           (Generated container config)
│       └── requirements.txt      (Python dependencies)
└── builds/
    └── {submission_id}/
        └── build_logs.txt       (Cloud Build output)
```

---

## 🏗️ CLOUD BUILD SETUP

### **Cloud Build Trigger** (Manual Setup Required)

You'll need to create a Cloud Build configuration for the demo:

**File**: `backend/cloudbuild.yaml` (to create)

```yaml
steps:
  # Step 1: Build Docker Image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/retro-fit-modernized:$BUILD_ID'
      - '-f'
      - 'Dockerfile'
      - '.'
    
  # Step 2: Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/retro-fit-modernized:$BUILD_ID'
    
  # Step 3: Deploy to Cloud Run (Optional)
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - run
      - --publish

images:
  - 'gcr.io/$PROJECT_ID/retro-fit-modernized:$BUILD_ID'

options:
  machineType: 'N1_HIGHCPU_8'

timeout: '1800s'
```

---

## 🔐 SECRETS MANAGEMENT (Production)

For production deployment on Google Cloud:

### **Create Secret in Secret Manager**
```bash
gcloud secrets create retro-fit-credentials \
  --replication-policy="automatic" \
  --data-file=backend/credentials.json
```

### **Grant Access to Cloud Run**
```bash
gcloud secrets add-iam-policy-binding retro-fit-credentials \
  --member=serviceAccount:PROJECT_ID@appspot.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### **Reference in Cloud Run**
```bash
gcloud run deploy retro-fit-backend \
  --set-secrets CREDENTIALS=/retro-fit-credentials:latest
```

---

## ✅ CREDENTIAL VERIFICATION CHECKLIST

Before deploying, verify:

- [ ] `credentials.json` exists at `backend/credentials.json`
- [ ] File is in `.gitignore` (won't be committed)
- [ ] `docker-compose.yml` mounts it correctly
- [ ] GCP Project ID matches `retro-fit-dev-485215`
- [ ] Service account has Storage, Cloud Build, Vertex AI permissions
- [ ] GCS bucket `retro-fit-dev-485215-uploads` exists
- [ ] All required APIs are enabled:
  - [ ] Cloud Storage
  - [ ] Cloud Build
  - [ ] Vertex AI
  - [ ] Cloud Run
  - [ ] Cloud Logging

---

## 🚀 LOCAL TESTING WITHOUT FULL CREDENTIALS

For quick local testing without GCP setup, use "**Simulation Mode**":

```python
# In backend/app/services/cloudbuild.py
USE_SIMULATE_MODE = True  # Set to False when using real GCP
```

This will:
- Mock Cloud Build responses
- Generate fake build logs
- Simulate pass/fail scenarios
- Still sanitize and process code locally

---

## 📋 DEMO DAY CREDENTIALS CHECKLIST

**Before the 3-minute demo:**

- [ ] credentials.json is in `backend/` and not committed to Git
- [ ] All GCP APIs are enabled (test via `gcloud services list --enabled`)
- [ ] GCS bucket is accessible (test: `gsutil ls gs://retro-fit-dev-485215-uploads/`)
- [ ] Cloud Build API works (test: `gcloud builds submit --async`)
- [ ] Vertex AI can generate content (test: run a quick Gemini call)
- [ ] Docker compose starts without credential errors
- [ ] Frontend can reach backend at `http://localhost:8000`
- [ ] Sample zombie code ZIP is ready in `samples/`

---

## 🆘 TROUBLESHOOTING

### **Error: "credentials.json not found"**
```bash
# Ensure file exists
ls -la backend/credentials.json

# Check Docker volume mount
docker-compose config | grep credentials

# Verify path in docker-compose.yml
cat docker-compose.yml | grep GOOGLE_APPLICATION_CREDENTIALS
```

### **Error: "Permission denied" from GCS**
```bash
# Verify service account has Storage Admin role
gcloud projects get-iam-policy retro-fit-dev-485215 \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/storage.*"
```

### **Error: "Vertex AI not initialized"**
```bash
# Verify Vertex AI API is enabled
gcloud services list --enabled | grep aiplatform

# If not enabled
gcloud services enable aiplatform.googleapis.com
```

### **Error: "Build submission failed"**
```bash
# Check Cloud Build logs
gcloud builds log --stream

# Verify service account has Cloud Build Editor role
gcloud projects get-iam-policy retro-fit-dev-485215 \
  --filter="bindings.role:roles/cloudbuild.*"
```

---

## 📞 QUICK REFERENCE

| Service | Project ID | Bucket Name | Region |
|---------|-----------|-------------|--------|
| GCP | `retro-fit-dev-485215` | `retro-fit-dev-485215-uploads` | `us-central1` |
| Vertex AI | ✅ Enabled | — | us-central1 |
| Cloud Build | ✅ Enabled | — | us-central1 |
| Cloud Storage | ✅ Enabled | ✅ Created | us-central1 |
| Cloud Run | ✅ Enabled | — | us-central1 |

---

**Last Updated**: January 23, 2026  
**Status**: Ready for Implementation

