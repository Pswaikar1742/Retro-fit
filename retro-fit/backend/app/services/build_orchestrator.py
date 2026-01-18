from typing import Any, Dict, Optional
import subprocess
import json
from fastapi import HTTPException

class BuildOrchestrator:
    def __init__(self, project_id: str, cloud_build_trigger_id: str):
        self.project_id = project_id
        self.cloud_build_trigger_id = cloud_build_trigger_id

    def trigger_build(self, source: Dict[str, Any]) -> str:
        try:
            build_response = subprocess.run(
                [
                    "gcloud",
                    "builds",
                    "submit",
                    "--project",
                    self.project_id,
                    "--trigger",
                    self.cloud_build_trigger_id,
                    "--source",
                    json.dumps(source)
                ],
                capture_output=True,
                text=True,
                check=True
            )
            return build_response.stdout
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Build failed: {e.stderr}")

    def parse_build_logs(self, logs: str) -> Optional[str]:
        # Implement log parsing logic to extract relevant error messages
        # This is a placeholder for actual log parsing
        return logs if "error" in logs else None

    def handle_build_result(self, build_logs: str) -> None:
        error_message = self.parse_build_logs(build_logs)
        if error_message:
            # Logic to handle errors, possibly retrying the build
            raise HTTPException(status_code=400, detail=f"Build error: {error_message}")

    def orchestrate_build(self, source: Dict[str, Any]) -> str:
        build_logs = self.trigger_build(source)
        self.handle_build_result(build_logs)
        return "Build succeeded"