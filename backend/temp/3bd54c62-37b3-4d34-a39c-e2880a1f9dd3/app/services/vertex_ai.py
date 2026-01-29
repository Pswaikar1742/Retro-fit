import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
from app.core.config import settings
import json
import asyncio

class VertexAIService:
    def __init__(self):
        # Initialize Vertex AI SDK
        # In production, this might be done in an async startup event
        vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_REGION)
        self.model = GenerativeModel("gemini-1.5-pro")

    async def generate_content(self, prompt: str, schema: dict | None = None) -> dict | str:
        """
        Sends a prompt to Gemini 1.5 Pro.
        If 'schema' is provided, it instructs the model to output JSON adhering to it.
        """
        try:
            full_prompt = prompt
            if schema:
                full_prompt += f"\n\nOutput STRICT JSON strictly adhering to this schema:\n{json.dumps(schema)}"

            # Run in threadpool because Vertex SDK is synchronous blocking logic
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config={
                    "temperature": 0.2, # Low temperature for code generation
                    "max_output_tokens": 8192,
                }
            )
            
            text = response.text
            
            # Simple JSON extraction helper
            if schema:
                return self._extract_json(text)
            
            return text

        except Exception as e:
            print(f"Vertex AI Error: {e}")
            raise e

    def _extract_json(self, text: str) -> dict:
        """
        Clean markdown code blocks ```json ... ``` if present
        """
        try:
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from AI response: {text[:100]}...")
            # Self-healing: In a real agent, we might recurse here asking AI to fix the JSON.
            raise ValueError("AI returned invalid JSON")

vertex_ai_service = VertexAIService()
