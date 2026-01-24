import logging
import json
import tempfile
import os
import zipfile
from typing import Dict, Any, Tuple, TYPE_CHECKING
from app.services.auditor import AnalysisReport

if TYPE_CHECKING:
    from app.services.vertexai_client import VertexAIClient
    from app.services.auditor import CodeAuditor
    from app.utils.json_parser import JSONParser

logger = logging.getLogger(__name__)


class CodeRefactorer:
    """
    Coordinates the refactoring process using Gemini and Cloud Build.
    Generates modernized code and Dockerfile for deployment.
    """

    def __init__(self):
        """Initialize refactorer with required clients."""
        # Lazy-load to avoid import hangs
        from app.services.vertexai_client import VertexAIClient
        from app.services.auditor import CodeAuditor
        from app.utils.json_parser import JSONParser
        
        self.gemini_client = VertexAIClient()
        self.auditor = CodeAuditor()
        self.json_parser = JSONParser()

    def refactor_code(
        self,
        code: str,
        filename: str = "code.py",
        analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Refactor code to Python 3.11 with modern patterns.

        Args:
            code: Source code to refactor
            filename: Original filename
            analysis: Pre-computed analysis (optional)

        Returns:
            Refactored code and Dockerfile
        """
        logger.info(f"Starting refactoring for {filename}")

        # Analyze if not provided
        if analysis is None:
            logger.info("Running code analysis...")
            analysis = self.auditor.analyze_code(code, filename)
        
        # Display analysis report
        report = AnalysisReport.format_for_display(analysis)
        logger.info(report)

        # Refactor based on analysis
        try:
            refactored = self.gemini_client.refactor_code(
                self._build_refactor_prompt(code, filename, analysis)
            )
            
            # Handle both dict and string responses
            if isinstance(refactored, dict):
                logger.debug(f"Refactored result (dict): {str(refactored)[:200]}...")
            else:
                logger.debug(f"Refactored result: {str(refactored)[:200]}...")

            return refactored

        except Exception as e:
            logger.error(f"Failed to refactor code: {e}")
            raise RuntimeError(f"Code refactoring failed: {e}")

    def generate_requirements_txt(
        self,
        analysis: Dict[str, Any],
        additional_packages: list = None
    ) -> str:
        """
        Generate requirements.txt based on analysis and patterns.

        Args:
            analysis: Analysis result with detected frameworks
            additional_packages: Extra packages to include

        Returns:
            requirements.txt content
        """
        logger.info("Generating requirements.txt")

        packages = set()

        # Base packages for all Python apps
        packages.update([
            "pydantic>=2.0.0",
            "python-dotenv>=1.0.0",
        ])

        # Framework-specific packages
        frameworks = analysis.get("frameworks", [])
        
        framework_packages = {
            "fastapi": ["fastapi>=0.104.0", "uvicorn>=0.24.0"],
            "django": ["django>=4.2.0", "gunicorn>=21.0.0"],
            "flask": ["flask>=3.0.0", "gunicorn>=21.0.0"],
            "asyncio": ["aiofiles>=23.0.0"],
            "pydantic": ["pydantic>=2.0.0"],
            "sqlalchemy": ["sqlalchemy>=2.0.0"],
        }

        for framework in frameworks:
            if framework.lower() in framework_packages:
                packages.update(framework_packages[framework.lower()])

        # Add additional packages
        if additional_packages:
            packages.update(additional_packages)

        # Sort and format
        sorted_packages = sorted(list(packages))
        content = "\n".join(sorted_packages)

        logger.info(f"Generated requirements.txt with {len(sorted_packages)} packages")
        return content

    def create_refactored_package(
        self,
        refactored_result: Dict[str, Any],
        original_files: Dict[str, str] = None
    ) -> Tuple[str, Dict[str, str]]:
        """
        Create a complete refactored package with all files.

        Args:
            refactored_result: Result from refactor_code
            original_files: Other files to include (e.g., config files)

        Returns:
            Path to generated ZIP file and file manifest
        """
        logger.info("Creating refactored package")

        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            files_created = {}

            # Write main refactored code
            code_filename = refactored_result.get("filename", "app.py")
            code_path = os.path.join(tmpdir, code_filename)
            with open(code_path, 'w') as f:
                f.write(refactored_result.get("refactored_code", ""))
            files_created[code_filename] = len(refactored_result.get("refactored_code", ""))

            # Write Dockerfile
            dockerfile_path = os.path.join(tmpdir, "Dockerfile")
            with open(dockerfile_path, 'w') as f:
                f.write(refactored_result.get("dockerfile", ""))
            files_created["Dockerfile"] = len(refactored_result.get("dockerfile", ""))

            # Write requirements.txt
            analysis = refactored_result.get("analysis", {})
            requirements = self.generate_requirements_txt(analysis)
            req_path = os.path.join(tmpdir, "requirements.txt")
            with open(req_path, 'w') as f:
                f.write(requirements)
            files_created["requirements.txt"] = len(requirements)

            # Add additional files if provided
            if original_files:
                for filename, content in original_files.items():
                    file_path = os.path.join(tmpdir, filename)
                    # Create subdirectories if needed
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(content)
                    files_created[filename] = len(content)

            # Create manifest
            manifest = {
                "original_file": refactored_result.get("filename"),
                "analysis": {
                    "total_issues": len(analysis.get("issues", [])),
                    "estimated_time_minutes": analysis.get("estimated_refactor_time_minutes"),
                    "python_version": analysis.get("python_version", "3.11"),
                },
                "changes_made": refactored_result.get("changes_made", []),
                "new_features": refactored_result.get("new_features", []),
                "breaking_changes": refactored_result.get("breaking_changes", []),
                "migration_notes": refactored_result.get("migration_notes", ""),
                "files_created": files_created,
            }

            # Write manifest
            manifest_path = os.path.join(tmpdir, "REFACTOR_MANIFEST.json")
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            files_created["REFACTOR_MANIFEST.json"] = len(json.dumps(manifest, indent=2))

            logger.info(f"Package created with {len(files_created)} files")
            return tmpdir, files_created

    def _build_refactor_prompt(
        self,
        code: str,
        filename: str,
        analysis: Dict[str, Any]
    ) -> str:
        """Build the refactoring prompt for Gemini."""
        issues_summary = "\n".join([
            f"  - {issue.get('type')}: {issue.get('description')}"
            for issue in analysis.get("issues", [])[:5]
        ])

        return f"""
Refactor this Python code ({filename}) to Python 3.11 with modern patterns.
Return ONLY a JSON response with this exact structure (no markdown, no extra text):

{{
  "refactored_code": "# Full refactored code here with type hints, async/await, etc.",
  "dockerfile": "FROM python:3.11-slim\n...",
  "changes_made": ["change1", "change2"],
  "new_features": ["feature1", "feature2"],
  "breaking_changes": [],
  "migration_notes": "Any migration steps needed"
}}

Original Issues Found:
{issues_summary}

Requirements:
- Python 3.11+
- Add type hints everywhere
- Use async/await where applicable
- Follow PEP 8
- Preserve all original functionality
- Add docstrings to functions

Original Code:
```python
{code}
```

Provide ONLY the JSON response, no additional text.
"""

    @staticmethod
    def _generate_default_dockerfile(python_filename: str) -> str:
        """Generate a default Dockerfile."""
        app_name = python_filename.replace(".py", "")
        return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "{python_filename}"]
"""

    @staticmethod
    def _validate_refactor_result(result: Dict[str, Any]) -> None:
        """Validate refactoring result structure."""
        required_keys = ["refactored_code", "dockerfile"]
        missing = [key for key in required_keys if key not in result]
        
        if missing:
            logger.warning(f"Refactor result missing keys: {missing}")
            raise ValueError(f"Invalid refactor result: missing {missing}")


class RefactorReport:
    """Helper class for formatting refactor results."""

    @staticmethod
    def format_summary(refactored_result: Dict[str, Any]) -> str:
        """Create a summary of refactoring changes."""
        lines = [
            "\n" + "=" * 60,
            "REFACTORING REPORT",
            "=" * 60,
            f"File: {refactored_result.get('filename', 'unknown')}",
            "",
            "CHANGES MADE:",
        ]

        for change in refactored_result.get("changes_made", [])[:8]:
            lines.append(f"  ✓ {change}")

        if refactored_result.get("new_features"):
            lines.append("\nNEW FEATURES:")
            for feature in refactored_result.get("new_features", [])[:8]:
                lines.append(f"  + {feature}")

        if refactored_result.get("breaking_changes"):
            lines.append("\n⚠️  BREAKING CHANGES:")
            for change in refactored_result.get("breaking_changes", []):
                lines.append(f"  ! {change}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
