from app.services.vertex_ai import vertex_ai_service
from app.models.schemas import AuditResult

class AuditorAgent:
    """
    Analyzes legacy code structure and identifies issues.
    """
    async def audit_codebase(self, file_structure: list[str], sample_code: str) -> AuditResult:
        prompt = f"""
        You are a Senior Software Architect. Analyze this legacy Python 2.7 application structure and code sample.
        
        File Structure:
        {file_structure}

        Sample Code (Main Entrypoint):
        {sample_code[:5000]} 

        Identify:
        1. The architectural style (Monolith, Script, etc.)
        2. Specific Python 2.7 deprecations (print statements, ConfigParser, etc.)
        3. Security risks.
        4. A strategy to modernize this to Python 3.11 + FastAPI + Docker.
        """

        # Define schema for strict output
        schema = {
            "type": "object",
            "properties": {
                "original_architecture": {"type": "string"},
                "detected_issues": {"type": "array", "items": {"type": "string"}},
                "modernization_strategy": {"type": "string"}
            },
            "required": ["original_architecture", "detected_issues", "modernization_strategy"]
        }

        response_dict = await vertex_ai_service.generate_content(prompt, schema=schema)
        
        return AuditResult(**response_dict)

auditor_agent = AuditorAgent()
