# Retro-Fit: Autonomous Legacy Code Modernization Platform

## Project Overview
Retro-Fit is an innovative platform designed to modernize legacy Python code, specifically targeting unmaintained scripts and applications. By leveraging a Multi-Agent AI system, Retro-Fit automates the process of sanitizing, refactoring, containerizing, and verifying legacy code, ensuring a seamless transition to modern standards.

## Features
1. **Sanitize**: Automatically removes Personally Identifiable Information (PII) and secrets from the uploaded code.
2. **Refactor**: Upgrades legacy Python 2.7 code to Python 3.11 standards.
3. **Containerize**: Generates a valid `Dockerfile` and `requirements.txt` for easy deployment.
4. **Verify**: Triggers a build in Google Cloud Build to validate the functionality of the refactored code.
5. **Self-Heal**: Implements a feedback loop where the AI analyzes build logs, fixes issues, and retries the build process if it fails.

## Tech Stack
- **Frontend**: Next.js 14, Tailwind CSS, Lucide React
- **Backend**: Python 3.11 (FastAPI)
- **AI Engine**: Google Vertex AI SDK (`gemini-1.5-pro`)
- **Infrastructure**:
  - Google Cloud Storage (GCS)
  - Google Cloud Build
  - Google Cloud Run
  - Google Pub/Sub (for async job queuing)

## Getting Started

### Prerequisites
- Python 3.11
- Node.js (for frontend)
- Docker
- Google Cloud account with necessary permissions

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd retro-fit
   ```

2. Set up the backend:
   - Navigate to the `backend` directory.
   - Create a `.env` file based on `.env.example` and configure your environment variables.
   - Install dependencies:
     ```
     pip install -r requirements.txt
     ```

3. Set up the frontend:
   - Navigate to the `frontend` directory.
   - Create a `.env.local` file based on `.env.local.example` and configure your environment variables.
   - Install dependencies:
     ```
     npm install
     ```

### Running the Application
- Start the backend:
  ```
  cd backend
  uvicorn app.main:app --reload
  ```

- Start the frontend:
  ```
  cd frontend
  npm run dev
  ```

### Usage
- Upload your legacy Python code as a ZIP file through the frontend interface.
- Monitor the status of the modernization process through the console output.
- Access the refactored code and Docker artifacts upon successful completion.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.