import logging
import time
from typing import Dict, Any, Optional
try:
    from google.cloud import build_v1
    HAS_BUILD_V1 = True
except ImportError:
    HAS_BUILD_V1 = False
    build_v1 = None
from app.core.config import settings

logger = logging.getLogger(__name__)


class CloudBuildService:
    """
    Google Cloud Build integration for verifying generated code.
    Triggers builds, monitors status, and retrieves logs.
    """

    def __init__(self, use_simulate_mode: bool = True):
        """
        Initialize Cloud Build service.

        Args:
            use_simulate_mode: If True, simulate responses without calling GCP
        """
        self.use_simulate_mode = use_simulate_mode
        self.project_id = settings.GCP_PROJECT_ID
        self.region = settings.GCP_REGION
        
        if self.use_simulate_mode:
            logger.info("Cloud Build service in simulate mode.")
        else:
            try:
                self.client = build_v1.CloudBuildClient()
                logger.info(f"Initialized Cloud Build client for project: {self.project_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize Cloud Build client: {e}")
                logger.info("Falling back to simulate mode")
                self.use_simulate_mode = True
                self.client = None

    def trigger_build(
        self,
        source_gcs_uri: str,
        dockerfile_path: str = "Dockerfile",
        image_tag: Optional[str] = None,
        timeout_seconds: int = 1800
    ) -> Dict[str, Any]:
        """
        Trigger a Cloud Build for the generated code.

        Args:
            source_gcs_uri: GCS path to source ZIP (e.g., gs://bucket/path/source.zip)
            dockerfile_path: Path to Dockerfile in source
            image_tag: Tag for built image (defaults to auto-generated)
            timeout_seconds: Build timeout in seconds

        Returns:
            Build information with build_id and status
        """
        if self.use_simulate_mode:
            return self._simulate_trigger_build(source_gcs_uri)

        try:
            logger.info(f"Triggering Cloud Build for {source_gcs_uri}")
            
            if not image_tag:
                image_tag = f"gcr.io/{self.project_id}/retro-fit-modernized:latest"

            # Build configuration
            build_config = {
                "source": {
                    "storage_source": {
                        "bucket": self._extract_bucket(source_gcs_uri),
                        "object": self._extract_object(source_gcs_uri),
                    }
                },
                "steps": [
                    {
                        "name": "gcr.io/cloud-builders/docker",
                        "args": ["build", "-t", image_tag, "-f", dockerfile_path, "."],
                    },
                    {
                        "name": "gcr.io/cloud-builders/docker",
                        "args": ["push", image_tag],
                    },
                ],
                "timeout": {"seconds": timeout_seconds},
                "images": [image_tag],
            }

            # Create build request
            request = build_v1.CreateBuildRequest(
                project_id=self.project_id,
                build=build_config,
            )

            # Submit build
            operation = self.client.create_build(request=request)
            build = operation.result()

            logger.info(f"Build submitted: {build.id}")
            return {
                "build_id": build.id,
                "status": "QUEUED",
                "image": image_tag,
                "source": source_gcs_uri,
            }

        except Exception as e:
            logger.error(f"Failed to trigger build: {e}")
            raise RuntimeError(f"Cloud Build trigger failed: {e}")

    def get_build_status(self, build_id: str) -> Dict[str, Any]:
        """
        Get current status of a build.

        Args:
            build_id: Build ID returned from trigger_build

        Returns:
            Build status information
        """
        if self.use_simulate_mode:
            return self._simulate_get_status(build_id)

        try:
            request = build_v1.GetBuildRequest(
                project_id=self.project_id,
                id=build_id,
            )
            
            build = self.client.get_build(request=request)

            status_map = {
                build_v1.Build.Status.QUEUED: "QUEUED",
                build_v1.Build.Status.WORKING: "WORKING",
                build_v1.Build.Status.SUCCESS: "SUCCESS",
                build_v1.Build.Status.FAILURE: "FAILURE",
                build_v1.Build.Status.TIMEOUT: "TIMEOUT",
                build_v1.Build.Status.CANCELLED: "CANCELLED",
            }

            status = status_map.get(build.status, "UNKNOWN")
            logger.info(f"Build {build_id} status: {status}")

            return {
                "build_id": build_id,
                "status": status,
                "create_time": build.create_time.isoformat() if build.create_time else None,
                "finish_time": build.finish_time.isoformat() if build.finish_time else None,
                "log_url": build.log_url,
            }

        except Exception as e:
            logger.error(f"Failed to get build status: {e}")
            raise RuntimeError(f"Failed to retrieve build status: {e}")

    def get_build_logs(self, build_id: str, max_lines: int = 500) -> str:
        """
        Retrieve build logs.

        Args:
            build_id: Build ID
            max_lines: Maximum number of log lines to retrieve

        Returns:
            Build log output
        """
        if self.use_simulate_mode:
            return self._simulate_get_logs(build_id)

        try:
            request = build_v1.GetBuildRequest(
                project_id=self.project_id,
                id=build_id,
            )
            
            build = self.client.get_build(request=request)

            if not build.log_url:
                logger.warning(f"No log URL available for build {build_id}")
                return "No logs available"

            # In production, you would fetch from Cloud Logging
            # For now, return a message with the log URL
            logger.info(f"Build logs available at: {build.log_url}")
            return f"Logs available at: {build.log_url}\n\nBuild Status: {build.status}"

        except Exception as e:
            logger.error(f"Failed to get build logs: {e}")
            raise RuntimeError(f"Failed to retrieve build logs: {e}")

    # Simulation mode methods for demo/testing without GCP
    def _simulate_trigger_build(self, source_uri: str) -> Dict[str, Any]:
        """Simulate a build trigger for testing."""
        import random
        import string
        
        build_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        logger.info(f"[SIMULATE] Triggered build: {build_id}")
        
        return {
            "build_id": build_id,
            "status": "QUEUED",
            "image": f"gcr.io/{self.project_id}/retro-fit-modernized:latest",
            "source": source_uri,
        }

    def _simulate_get_status(self, build_id: str) -> Dict[str, Any]:
        """Simulate getting build status."""
        # For demo purposes, show realistic progression
        # In real usage, this would query actual build status
        statuses = ["QUEUED", "WORKING", "SUCCESS"]
        
        # Use build_id hash to determine simulated status
        status_index = (hash(build_id) % len(statuses))
        status = statuses[status_index]
        
        logger.info(f"[SIMULATE] Build {build_id} status: {status}")
        
        return {
            "build_id": build_id,
            "status": status,
            "create_time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime()),
            "finish_time": None if status != "SUCCESS" else time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime()),
            "log_url": f"https://console.cloud.google.com/cloud-build/builds/{build_id}",
        }

    def _simulate_get_logs(self, build_id: str) -> str:
        """Simulate build logs for testing."""
        logs = f"""
=== Cloud Build Logs (Simulated) ===
Build ID: {build_id}
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}

Step 1/2: Building Docker image
  FROM python:3.11-slim
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . /app
  WORKDIR /app
  CMD ["python", "app.py"]
  
  ✓ Image built successfully: gcr.io/{self.project_id}/retro-fit-modernized:latest

Step 2/2: Pushing to container registry
  ✓ Image pushed to GCR

Build completed successfully!
Total build time: 2m 34s
        """
        logger.info(f"[SIMULATE] Returning simulated logs for build {build_id}")
        return logs

    @staticmethod
    def _extract_bucket(gcs_uri: str) -> str:
        """Extract bucket name from GCS URI (gs://bucket/path)."""
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        return parts[0]

    @staticmethod
    def _extract_object(gcs_uri: str) -> str:
        """Extract object path from GCS URI (gs://bucket/path)."""
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        return parts[1] if len(parts) > 1 else ""


# Global singleton instance
_build_service_instance: Optional[CloudBuildService] = None


def get_cloud_build_service(use_simulate: bool = False) -> CloudBuildService:
    """
    Get or create the Cloud Build service singleton.

    Args:
        use_simulate: Force simulate mode
    """
    global _build_service_instance
    if _build_service_instance is None:
        _build_service_instance = CloudBuildService(use_simulate_mode=use_simulate)
    return _build_service_instance
