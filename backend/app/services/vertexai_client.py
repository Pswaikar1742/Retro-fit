import os
import logging
from typing import Dict, Any, Optional
import requests

# Lazy-load Vertex AI to avoid import hangs
try:
    import google.generativeai as local_ai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    HAS_VERTEXAI = True
except ImportError:
    HAS_VERTEXAI = False
    local_ai = None
    GenerativeModel = None
    GenerationConfig = None

from app.core.config import settings
from app.utils.json_parser import JSONParser

logger = logging.getLogger(__name__)


class VertexAIClient:
    """
    Wrapper for Google Vertex AI Gemini model.
    Provides methods for code analysis, refactoring, and self-healing.
    Falls back to simulation mode when GCP credentials aren't available.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Vertex AI client with specified model.

        Args:
            model_name: Model name (defaults to settings.VERTEX_AI_MODEL)
        """
        self.model_name = model_name or settings.VERTEX_AI_MODEL
        self.temperature = settings.VERTEX_AI_TEMPERATURE
        self.model = None
        self.simulation_mode = False

        self.api_key = os.getenv("GEMINI_API_KEY")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.ollama_model = os.getenv("OLLAMA_MODEL")
        self.mode = "simulation"

        if self.ollama_model:
            self.mode = "ollama"
            logger.info(f"Using Ollama model: {self.ollama_model}.")
        elif self.api_key and local_ai:
            self.mode = "local"
            local_ai.configure(api_key=self.api_key)
            logger.info("Using Local AI with GEMINI_API_KEY.")
        elif self.credentials_path and HAS_VERTEXAI:
            self.mode = "cloud"
            vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))
            logger.info("Using Vertex AI with GOOGLE_APPLICATION_CREDENTIALS.")
        else:
            logger.warning("No valid AI configuration found. Falling back to Simulation Mode.")

        self.simulation_mode = self.mode == "simulation"

    def _simulate_analysis_response(self):
        """Simulate a valid analysis response."""
        response = {
            "filename": "main.py",
            "issues": [],
            "patterns": [],
            "recommendation": "No issues found. Code is modern and follows best practices.",
            "python_version": "3.11",
            "frameworks": [],
            "estimated_refactor_time_minutes": 0
        }
        logger.debug(f"Simulated analysis response: {response}")
        return response

    def analyze_code(self, code_context: str) -> Dict[str, Any]:
        """
        Analyze legacy code structure and identify issues.

        Args:
            code_context: Full code content or code samples

        Returns:
            Analysis with architecture, issues, and recommendations
        """
        prompt = f"""
You are a Senior Python Code Architect and Legacy System Expert.
Analyze the following code and provide a detailed assessment.

CODE:
{code_context}

Provide your response as a JSON object with these keys:
- "filename": Original filename
- "architecture": Description of current architecture/design
- "issues": List of identified problems (max 10)
- "patterns": List of detected patterns
- "python_version": Detected Python version
- "frameworks": List of detected frameworks
- "recommendation": High-level modernization strategy

Response format (JSON only):
{{
    "filename": "...",
    "architecture": "...",
    "issues": ["issue1", "issue2"],
    "patterns": ["pattern1", "pattern2"],
    "python_version": "2.7 or 3.x",
    "frameworks": ["flask", "django"],
    "recommendation": "..."
}}
        """

        try:
            logger.info("Calling Gemini for code analysis...")
            if self.simulation_mode:
                logger.info("Using SIMULATION mode for Gemini response")
                return self._simulate_analysis_response()

            response = self._call_gemini(prompt)

            # If response is already a dict (from simulation mode), use directly
            if isinstance(response, dict):
                result = response
            else:
                result = JSONParser.extract_json(response)
            logger.info(f"Code analysis complete. Issues found: {len(result.get('issues', []))}")
            return result
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return mock analysis on failure
            return {
                "filename": "unknown",
                "architecture": "Unknown - Analysis failed",
                "issues": [{"type": "ERROR", "severity": "HIGH", "description": "Unable to analyze code"}],
                "patterns": ["unknown"],
                "python_version": "unknown",
                "frameworks": [],
                "recommendation": "Manual review recommended"
            }

    def refactor_code(self, code_context: str) -> Dict[str, str]:
        """
        Refactor legacy code to modern Python 3.11 standards.

        Args:
            code_context: Full code content or samples

        Returns:
            Dictionary with refactored_code and dockerfile
        """
        prompt = f"""
You are a Senior Python Architect specializing in modernization.
Refactor the following Legacy Python 2/3 code to modern Python 3.11+ standards.
Also generate a production-ready Dockerfile.

LEGACY CODE:
{code_context}

REQUIREMENTS:
1. Modernize to Python 3.11+ (fix print statements, imports, string handling, etc.)
2. Add type hints where applicable
3. Use modern async/await patterns if relevant
4. Create a production-ready Dockerfile using python:3.11-slim
5. Include requirements.txt in the Dockerfile

Return as JSON (NO MARKDOWN, PURE JSON):
{{
    "refactored_code": "# Full refactored code here",
    "dockerfile": "FROM python:3.11-slim\\n..."
}}
        """

        try:
            logger.info("Calling Gemini for code refactoring...")
            response = self._call_gemini(prompt)

            # If response is already a dict (from simulation mode), use directly
            if isinstance(response, dict):
                result = response
            else:
                result = JSONParser.extract_json(
                    response,
                    fallback_mock={
                        "refactored_code": '''#!/usr/bin/env python3
"""Modernized Python 3.11+ Application - Generated by Retro-Fit"""
from typing import Optional
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_user_input(prompt: str) -> str:
    """Get user input with type hints."""
    return input(prompt)


async def main() -> None:
    """Main entry point with async support."""
    logger.info("Application started - Modernized by Retro-Fit")
    name: str = await get_user_input("Enter your name: ")
    print(f"Hello, {name}! Welcome to Python 3.11+")
    logger.info("Application completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
''',
                        "dockerfile": """# Production Dockerfile - Generated by Retro-Fit
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["python", "app.py"]
"""
                    }
                )

            # Validate response structure
            JSONParser.validate_refactor_response(result)
            logger.info("Code refactoring complete")
            return result
        except Exception as e:
            logger.error(f"Refactoring failed: {e}")
            raise

    def fix_code_from_logs(self, original_code: str, error_logs: str, iteration: int = 1) -> Dict[str, str]:
        """
        Self-healing: Fix code based on build error logs.

        Args:
            original_code: Previously generated code that failed to build
            error_logs: Build error output from Cloud Build
            iteration: Which retry attempt this is (for logging)

        Returns:
            Dictionary with fixed refactored_code and dockerfile
        """
        # Extract structured error information
        error_info = JSONParser.extract_error_info(error_logs)

        prompt = f"""
You are a Python expert debugging build failures.
The following code failed to build. Fix it based on the error logs.

ORIGINAL CODE:
{original_code[:2000]}  # Limit context

ERROR INFORMATION:
Type: {error_info['error_type']}
Message: {error_info['error_message']}
Full logs:
{error_logs[:1000]}

TASK:
1. Identify what caused the build failure
2. Fix the code to resolve the error
3. Ensure it still meets the original requirements
4. Update the Dockerfile if needed
5. Return ONLY valid JSON

Return as JSON (NO MARKDOWN):
{{
    "refactored_code": "# Fixed code here",
    "dockerfile": "FROM python:3.11-slim\\n...",
    "fix_explanation": "Brief explanation of what was fixed"
}}
        """

        try:
            logger.info(f"Self-healing attempt {iteration}: Calling Gemini with error context...")
            response = self._call_gemini(prompt)

            result = JSONParser.extract_json(response)

            # Validate response
            if "refactored_code" not in result or "dockerfile" not in result:
                raise ValueError("Fix response missing required fields")

            logger.info(f"Self-healing iteration {iteration} complete: {result.get('fix_explanation', 'N/A')}")
            return result
        except Exception as e:
            logger.error(f"Self-healing fix failed at iteration {iteration}: {e}")
            raise

    def _call_gemini(self, prompt: str, max_retries: int = 2) -> str:
        """
        Call Gemini API with retry logic and error handling.

        Args:
            prompt: Prompt to send to Gemini
            max_retries: Number of retries on failure

        Returns:
            Response text from Gemini

        Raises:
            RuntimeError: If all retry attempts fail
        """
        # Simulation mode - return mock response
        if self.mode == "ollama":
            return self._call_ollama(prompt)

        if self.simulation_mode or self.model is None:
            logger.info("Using SIMULATION mode for Gemini response")
            return self._get_simulated_response(prompt)

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Gemini API call (attempt {attempt + 1}/{max_retries + 1})")

                response = self.model.generate_content(
                    prompt,
                    generation_config=GenerationConfig(
                        response_mime_type="application/json",
                        temperature=self.temperature,
                        max_output_tokens=4096
                    )
                )

                if not response or not response.text:
                    raise ValueError("Empty response from Gemini")

                logger.debug(f"Received response ({len(response.text)} chars)")
                return response.text

            except Exception as e:
                last_error = e
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {e}")

                if attempt < max_retries:
                    import time
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("All Gemini API attempts exhausted")

        # All retries failed
        raise RuntimeError(f"Gemini API call failed after {max_retries + 1} attempts: {last_error}")

    def _get_simulated_response(self, prompt: str) -> dict:
        """Generate simulated response for demo mode. Returns dict directly."""

        # Detect what kind of request this is based on prompt
        if "refactor" in prompt.lower() or "modernize" in prompt.lower():
            return {
                "refactored_code": """#!/usr/bin/env python3
\"\"\"
Modernized Python 3.11+ Application
Auto-generated by Retro-Fit AI Modernization Platform
\"\"\"
from typing import Optional
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    \"\"\"Main entry point with async support.\"\"\"
    logger.info("Application started - Modernized by Retro-Fit")
    print("Hello from Python 3.11+!")

    # Simulated async operation
    await asyncio.sleep(0.1)
    logger.info("Application completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
""",
                "dockerfile": """# Production Dockerfile - Generated by Retro-Fit
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["python", "app.py"]
""",
                "fix_explanation": "Modernized to Python 3.11+ with async support, type hints, and logging"
            }
        elif any(keyword in prompt.lower() for keyword in ["analyze", "analysis", "audit", "issues", "recommendation"]):
            return {
                "filename": "legacy_code.py",
                "architecture": "Legacy monolithic Python application",
                "issues": [
                    {
                        "type": "LEGACY_PATTERN",
                        "severity": "HIGH",
                        "line_number": 1,
                        "description": "Python 2 print statements detected",
                        "suggestion": "Convert to Python 3 print() function"
                    },
                    {
                        "type": "MISSING_TYPES",
                        "severity": "MEDIUM",
                        "line_number": 5,
                        "description": "Missing type hints",
                        "suggestion": "Add type annotations for better code quality"
                    },
                    {
                        "type": "SYNC_CODE",
                        "severity": "MEDIUM",
                        "line_number": 10,
                        "description": "No async/await patterns",
                        "suggestion": "Consider using async for I/O operations"
                    },
                    {
                        "type": "OUTDATED_SYNTAX",
                        "severity": "LOW",
                        "line_number": 15,
                        "description": "Outdated string formatting",
                        "suggestion": "Use f-strings for cleaner formatting"
                    },
                    {
                        "type": "ERROR_HANDLING",
                        "severity": "HIGH",
                        "line_number": 20,
                        "description": "Missing error handling",
                        "suggestion": "Add try/except blocks for robustness"
                    }
                ],
                "patterns": ["synchronous_io", "outdated_imports", "legacy_print", "no_type_hints"],
                "python_version": "2.7",
                "frameworks": ["none"],
                "recommendation": "Full modernization to Python 3.11+ recommended. Focus on type hints, async patterns, and modern syntax.",
                "difficulty_score": 6,
                "estimated_refactor_time_minutes": 45
            }
        else:
            return {
                "status": "simulated",
                "message": "Response generated in simulation mode"
            }

    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama local model (local-first).

        Returns:
            Response text from Ollama
        """
        if not self.ollama_model:
            raise RuntimeError("OLLAMA_MODEL not set for Ollama mode")

        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        url = f"{host}/api/generate"
        
        # Enhanced prompt to ensure JSON output
        json_prompt = f"""{prompt}

IMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no explanations outside JSON.
"""
        
        payload = {
            "model": self.ollama_model,
            "prompt": json_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 4096
            }
        }

        try:
            logger.info(f"Calling Ollama model: {self.ollama_model}")
            response = requests.post(url, json=payload, timeout=180)  # Increased timeout for local models
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "")
            if not response_text:
                raise ValueError("Empty response from Ollama")
            logger.debug(f"Ollama response: {response_text[:200]}...")
            return response_text
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out - model may need more time")
            raise RuntimeError("Ollama request timed out")
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise

    @staticmethod
    def get_model_info() -> Dict[str, str]:
        """Get information about the configured model."""
        return {
            "model": settings.VERTEX_AI_MODEL,
            "temperature": str(settings.VERTEX_AI_TEMPERATURE),
            "region": settings.GCP_REGION,
            "project": settings.GCP_PROJECT_ID,
        }


# Global singleton instance
_client_instance: Optional[VertexAIClient] = None


def get_vertex_ai_client() -> VertexAIClient:
    """Get or create the Vertex AI client singleton."""
    global _client_instance
    if _client_instance is None:
        _client_instance = VertexAIClient()
    return _client_instance
