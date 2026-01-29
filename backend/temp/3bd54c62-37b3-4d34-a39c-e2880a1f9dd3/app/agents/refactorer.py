from app.services.vertex_ai import vertex_ai_service
from app.models.schemas import RefactorResult

class RefactorAgent:
    """
    Converts legacy code to Python 3.11 and generates Docker configurations.
    """
    async def refactor_code(self, filename: str, code_content: str, audit_context: str) -> dict:
        prompt = f"""
        You are an Expert Python Developer.
        Task: Refactor this legacy Python 2 code to Modern Python 3.11.
        Context: {audit_context}
        
        Target Standards:
        - Use Type Hints.
        - Use 'pydantic' if data structures are found.
        - Ensure UTF-8 encoding.
        - Fix all print() statements.
        
        Filename: {filename}
        Original Code:
        {code_content}
        
        Output ONLY the refactored code (no markdown, no explanations) inside the JSON field 'refactored_code'.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "refactored_code": {"type": "string"}
            },
            "required": ["refactored_code"]
        }

        return await vertex_ai_service.generate_content(prompt, schema=schema)

    async def generate_dockerfile(self, file_list: list[str]) -> str:
        prompt = f"""
        Generate a production-ready Dockerfile for a Python 3.11 app.
        Files in project: {file_list}
        
        Requirements:
        - Base image: python:3.11-slim
        - Workdir: /app
        - Install dependencies (requirements.txt)
        - Expose port 8000 (if web app detected) or just CMD ["python", "app.py"]
        - Use non-root user for security.
        """
        
        return await vertex_ai_service.generate_content(prompt)

refactor_agent = RefactorAgent()
