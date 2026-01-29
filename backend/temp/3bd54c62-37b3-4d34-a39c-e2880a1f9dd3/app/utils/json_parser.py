import json
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class JSONParser:
    """
    Robust JSON parser for handling Gemini AI responses.
    Handles markdown code blocks, extra whitespace, and malformed JSON.
    """

    @staticmethod
    def extract_json(response_text: str, fallback_mock: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract JSON from AI response, handling various formatting issues.

        Args:
            response_text: Raw response text from Gemini
            fallback_mock: Optional fallback data if parsing fails completely

        Returns:
            Parsed JSON dictionary
            
        Raises:
            ValueError: If JSON cannot be extracted or parsed
        """
        if not response_text or not isinstance(response_text, str):
            logger.error(f"Invalid response text: {type(response_text)}")
            if fallback_mock:
                logger.warning("Using fallback mock data")
                return fallback_mock
            raise ValueError("Response text is empty or invalid")

        # Try to clean and parse the response
        cleaned = JSONParser._clean_response(response_text)
        
        try:
            parsed = json.loads(cleaned)
            logger.info("Successfully parsed JSON from response")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Cleaned text: {cleaned[:200]}...")
            
            # Try alternative extraction methods
            alternative = JSONParser._extract_json_object(response_text)
            if alternative:
                logger.info("Successfully extracted JSON using alternative method")
                return alternative
            
            if fallback_mock:
                logger.warning("Using fallback mock data after all parsing attempts failed")
                return fallback_mock
            
            raise ValueError(f"Failed to extract valid JSON from response: {str(e)}")

    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove markdown code blocks and extra whitespace."""
        # Remove markdown code block wrappers
        if text.startswith("```json"):
            text = text[7:]  # Remove ```json
        if text.startswith("```"):
            text = text[3:]  # Remove ```
        if text.endswith("```"):
            text = text[:-3]  # Remove trailing ```
        
        # Strip whitespace
        text = text.strip()
        
        # Handle escaped newlines
        text = text.replace("\\n", "\n")
        
        return text

    @staticmethod
    def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON object from text using regex.
        Looks for patterns like {...} or similar.
        """
        # Find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        
        if start == -1 or end == -1 or start > end:
            logger.debug("No JSON object braces found")
            return None
        
        try:
            json_str = text[start:end+1]
            parsed = json.loads(json_str)
            logger.info("Extracted JSON using brace matching")
            return parsed
        except json.JSONDecodeError as e:
            logger.debug(f"Brace matching failed: {e}")
            return None

    @staticmethod
    def validate_refactor_response(data: Dict[str, Any]) -> bool:
        """
        Validate that the response contains required keys for refactoring.

        Returns:
            True if valid, raises ValueError otherwise
        """
        required_keys = {"refactored_code", "dockerfile"}
        
        if not isinstance(data, dict):
            raise ValueError(f"Response must be a dictionary, got {type(data)}")
        
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")
        
        # Validate that values are non-empty strings
        for key in required_keys:
            if not isinstance(data[key], str) or not data[key].strip():
                raise ValueError(f"Key '{key}' must be a non-empty string")
        
        logger.info("Response validation passed")
        return True

    @staticmethod
    def extract_error_info(error_text: str) -> Dict[str, str]:
        """
        Extract structured error information from build logs.
        Used for self-healing feedback to the AI.

        Returns:
            Dictionary with error details
        """
        error_info = {
            "raw_error": error_text,
            "error_type": "unknown",
            "error_message": "",
            "line_number": None,
        }

        # Try to identify error type
        error_types = {
            "ModuleNotFoundError": "missing_module",
            "ImportError": "import_error",
            "SyntaxError": "syntax_error",
            "IndentationError": "indentation_error",
            "TypeError": "type_error",
            "AttributeError": "attribute_error",
            "NameError": "name_error",
            "KeyError": "key_error",
            "ValueError": "value_error",
            "FileNotFoundError": "file_not_found",
        }

        for error_name, error_type in error_types.items():
            if error_name in error_text:
                error_info["error_type"] = error_type
                break

        # Try to extract line number
        line_match = re.search(r"line (\d+)", error_text, re.IGNORECASE)
        if line_match:
            error_info["line_number"] = int(line_match.group(1))

        # Extract first line of error message
        lines = error_text.split("\n")
        if lines:
            error_info["error_message"] = lines[0][:200]

        logger.info(f"Extracted error info: type={error_info['error_type']}")
        return error_info
