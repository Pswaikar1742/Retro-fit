import logging
from typing import Dict, Any, Optional

# Lazy-load Vertex AI to avoid import hangs
try:
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    HAS_VERTEXAI = True
except ImportError:
    HAS_VERTEXAI = False
    GenerativeModel = None
    GenerationConfig = None

from app.core.config import settings
from app.utils.json_parser import JSONParser

logger = logging.getLogger(__name__)


class VertexAIClient:
    """
    Wrapper for Google Vertex AI Gemini model.
    Provides methods for code analysis, refactoring, and self-healing.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Vertex AI client with specified model.

        Args:
            model_name: Model name (defaults to settings.VERTEX_AI_MODEL)
        """
        if not HAS_VERTEXAI:
            logger.warning("Vertex AI not available, client will use mock responses")
            self.model = None
            self.model_name = model_name or settings.VERTEX_AI_MODEL
            self.temperature = settings.VERTEX_AI_TEMPERATURE
            return
            
        self.model_name = model_name or settings.VERTEX_AI_MODEL
        self.model = GenerativeModel(self.model_name)
        self.temperature = settings.VERTEX_AI_TEMPERATURE
        logger.info(f"Initialized Vertex AI client with model: {self.model_name}")

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
- "architecture": Description of current architecture/design
- "issues": List of identified problems (max 10)
- "python_version": Detected Python version
- "frameworks": List of detected frameworks
- "recommendation": High-level modernization strategy

Response format (JSON only):
{{
    "architecture": "...",
    "issues": ["issue1", "issue2"],
    "python_version": "2.7 or 3.x",
    "frameworks": ["flask", "django"],
    "recommendation": "..."
}}
        """

        try:
            logger.info("Calling Gemini for code analysis...")
            response = self._call_gemini(prompt)
            
            result = JSONParser.extract_json(response)
            logger.info(f"Code analysis complete. Issues found: {len(result.get('issues', []))}")
            return result
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return mock analysis on failure
            return {
                "architecture": "Unknown - Analysis failed",
                "issues": ["Unable to analyze code"],
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
            
            result = JSONParser.extract_json(
                response,
                fallback_mock={
                    "refactored_code": "print('Hello Python 3.11')",
                    "dockerfile": "FROM python:3.11-slim\nCMD ['python', 'app.py']"
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
