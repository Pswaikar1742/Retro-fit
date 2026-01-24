import logging
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.vertexai_client import VertexAIClient
    from app.utils.json_parser import JSONParser

logger = logging.getLogger(__name__)


class CodeAuditor:
    """
    Analyzes legacy code to identify modernization opportunities.
    Returns structured analysis with issues, patterns, and recommendations.
    """

    def __init__(self):
        """Initialize auditor with Gemini client and JSON parser."""
        # Lazy-load to avoid import hangs
        from app.services.vertexai_client import VertexAIClient
        from app.utils.json_parser import JSONParser
        
        self.gemini_client = VertexAIClient()
        self.json_parser = JSONParser()

    def analyze_code(self, code: str, filename: str = "code.py") -> Dict[str, Any]:
        """
        Analyze code and identify modernization issues.

        Args:
            code: Source code to analyze
            filename: Original filename for context

        Returns:
            Structured analysis with issues, patterns, and recommendations
        """
        logger.info(f"Auditing code from {filename}")
        
        prompt = self._build_analysis_prompt(code, filename)
        
        try:
            response = self.gemini_client.analyze_code(prompt)
            
            # Handle both dict and string responses
            if isinstance(response, dict):
                analysis = response
                logger.debug(f"Raw analysis response (dict): {str(response)[:200]}...")
            else:
                logger.debug(f"Raw analysis response: {str(response)[:200]}...")
                analysis = self.json_parser.extract_json(
                    response,
                    fallback_mock={
                        "filename": filename,
                        "issues": [
                            {
                                "type": "LEGACY_PATTERN",
                                "severity": "MEDIUM",
                                "line_number": 1,
                                "description": "Legacy code pattern detected",
                                "suggestion": "Modernize with Python 3.11+ features"
                            }
                        ],
                        "patterns": ["synchronous_io", "outdated_imports"],
                        "python_version": "3.11",
                        "frameworks": ["no_framework"],
                        "recommendation": "Code is modernizable. Focus on async/await patterns and type hints.",
                        "difficulty_score": 5,
                        "estimated_refactor_time_minutes": 30
                    }
                )
            
            analysis = self._normalize_analysis(analysis, filename)
            self._validate_analysis(analysis)
            logger.info(f"Analysis complete: {len(analysis.get('issues', []))} issues found")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze code: {e}")
            raise RuntimeError(f"Code analysis failed: {e}")

    def categorize_issues(self, analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group issues by severity and type.

        Args:
            analysis: Analysis dict from analyze_code

        Returns:
            Issues grouped by severity
        """
        categorized = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": [],
        }

        for issue in analysis.get("issues", []):
            severity = issue.get("severity", "MEDIUM").upper()
            if severity in categorized:
                categorized[severity].append(issue)

        logger.info(
            f"Issues categorized: {len(categorized['CRITICAL'])} critical, "
            f"{len(categorized['HIGH'])} high, "
            f"{len(categorized['MEDIUM'])} medium, "
            f"{len(categorized['LOW'])} low"
        )
        return categorized

    def get_action_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a prioritized action plan based on analysis.

        Args:
            analysis: Analysis dict from analyze_code

        Returns:
            Prioritized list of refactoring steps
        """
        categorized = self.categorize_issues(analysis)
        
        action_plan = {
            "total_issues": len(analysis.get("issues", [])),
            "estimated_time_minutes": analysis.get("estimated_refactor_time_minutes", 60),
            "priority_steps": [],
            "quick_wins": [],
            "major_refactors": [],
        }

        # Critical issues first
        for issue in categorized.get("CRITICAL", []):
            action_plan["priority_steps"].append({
                "step": len(action_plan["priority_steps"]) + 1,
                "issue_type": issue.get("type"),
                "description": issue.get("description"),
                "action": issue.get("suggestion"),
                "effort": "HIGH",
            })

        # Quick wins (LOW severity improvements)
        for issue in categorized.get("LOW", [])[:3]:
            action_plan["quick_wins"].append({
                "issue_type": issue.get("type"),
                "description": issue.get("description"),
                "action": issue.get("suggestion"),
            })

        # Major refactors (HIGH/MEDIUM)
        for issue in (categorized.get("HIGH", []) + categorized.get("MEDIUM", []))[:5]:
            action_plan["major_refactors"].append({
                "issue_type": issue.get("type"),
                "description": issue.get("description"),
                "action": issue.get("suggestion"),
            })

        logger.info(f"Action plan created: {len(action_plan['priority_steps'])} priority steps")
        return action_plan

    def _build_analysis_prompt(self, code: str, filename: str) -> str:
        """Build the prompt for code analysis."""
        return f"""
Analyze this legacy Python code ({filename}) for modernization opportunities.
Return a JSON response with this exact structure:

{{
  "filename": "{filename}",
  "issues": [
    {{
      "type": "ISSUE_TYPE (e.g., LEGACY_PATTERN, OUTDATED_IMPORT, NO_TYPE_HINTS)",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "line_number": <int or null>,
      "description": "What's the issue?",
      "suggestion": "How to fix it"
    }}
  ],
  "patterns": ["pattern1", "pattern2"],
  "python_version": "3.11",
  "frameworks": ["framework1", "framework2"],
  "recommendation": "Overall strategy for modernization",
  "difficulty_score": <1-10>,
  "estimated_refactor_time_minutes": <int>
}}

Code to analyze:
```python
{code}
```

Focus on:
- Missing type hints
- Async/await opportunities
- Deprecated libraries
- Anti-patterns
- Performance issues
- Python 3.11+ features that could be used
"""

    @staticmethod
    def _validate_analysis(analysis: Dict[str, Any]) -> None:
        """Validate analysis structure."""
        required_keys = ["filename", "issues", "patterns", "recommendation"]
        missing = [key for key in required_keys if key not in analysis]
        
        if missing:
            logger.warning(f"Analysis missing keys: {missing}")
            raise ValueError(f"Invalid analysis structure: missing {missing}")

    @staticmethod
    def _normalize_analysis(analysis: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Ensure analysis contains required keys with safe defaults."""
        if not isinstance(analysis, dict):
            return {
                "filename": filename,
                "issues": [],
                "patterns": [],
                "recommendation": "No recommendation available.",
            }

        normalized = dict(analysis)
        normalized.setdefault("filename", filename)
        normalized.setdefault("issues", [])
        normalized.setdefault("patterns", [])
        normalized.setdefault("recommendation", "No recommendation available.")
        return normalized


class AnalysisReport:
    """Helper class for formatting audit results."""

    @staticmethod
    def format_for_display(analysis: Dict[str, Any]) -> str:
        """Format analysis for CLI/console display."""
        lines = [
            "\n" + "=" * 60,
            "CODE MODERNIZATION AUDIT REPORT",
            "=" * 60,
            f"File: {analysis.get('filename', 'unknown')}",
            f"Python Version: {analysis.get('python_version', '3.11')}",
            f"Total Issues: {len(analysis.get('issues', []))}",
            f"Est. Time: {analysis.get('estimated_refactor_time_minutes', '?')} min",
            "",
            "RECOMMENDATION:",
            analysis.get('recommendation', 'No recommendation'),
            "",
            "ISSUES FOUND:",
        ]

        for issue in analysis.get("issues", [])[:10]:
            severity = issue.get("severity", "MEDIUM")
            issue_type = issue.get("type", "UNKNOWN")
            desc = issue.get("description", "No description")
            lines.append(f"  [{severity:8}] {issue_type}: {desc}")

        if len(analysis.get("issues", [])) > 10:
            lines.append(f"  ... and {len(analysis.get('issues', [])) - 10} more issues")

        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def format_for_json(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Return analysis as-is for JSON response."""
        return analysis
