from typing import Any, Dict
import json
import requests

class AIAgent:
    def __init__(self, api_url: str, api_key: str) -> None:
        self.api_url = api_url
        self.api_key = api_key

    def analyze_architecture(self, code_context: str) -> Dict[str, Any]:
        prompt = {"prompt": f"Analyze this architecture: {code_context}"}
        response = self._send_request(prompt)
        return response

    def refactor_code(self, code_context: str) -> Dict[str, Any]:
        prompt = {"prompt": f"Refactor to Python 3 and write a Dockerfile. Output JSON."}
        response = self._send_request(prompt)
        return response

    def _send_request(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.api_url, headers=headers, json=prompt)
        response.raise_for_status()
        return response.json()