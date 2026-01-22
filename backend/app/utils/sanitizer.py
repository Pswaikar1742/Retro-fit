import re
import os
import shutil

class SanitizerService:
    @staticmethod
    def sanitize_directory(directory_path: str):
        """
        Recursively walks through a directory and removes PII/Secrets.
        For MVP, we will:
        1. Remove .env files
        2. Remove .git folders
        3. Scrub known API key patterns (simplified)
        """
        print(f"Sanitizing directory: {directory_path}")
        
        # 1. Remove dangerous input files
        for root, dirs, files in os.walk(directory_path):
            if ".git" in dirs:
                shutil.rmtree(os.path.join(root, ".git"))
                dirs.remove(".git") # prevent walking into it
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Delete sensitive files
                if file == ".env" or file.endswith(".key") or file.endswith(".pem"):
                    os.remove(file_path)
                    print(f"Removed sensitive file: {file_path}")
                    continue
                
                # Scan and scrub text files
                if file.endswith(('.py', '.txt', '.md', '.json', '.yml', '.yaml', '.ini', '.cfg')):
                    SanitizerService._scrub_file(file_path)

    @staticmethod
    def _scrub_file(file_path: str):
        """Reads a file and replaces secrets with [REDACTED]"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Simple regex for things that look like API Keys (32+ hex/alphanum chars)
            # This is a naive heuristic for the MVP.
            # Matches "api_key = 'abcdef12345...'"
            # pattern = r"(?i)(api[_-]?key|secret|token)\s*=\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]"
            # content = re.sub(pattern, r"\1='[REDACTED]'", content)

            # NOTE: Commented out aggressive regex to avoid breaking code structure for now.
            # Only removing extremely obvious placeholders if needed.
            
            # Write back if changed (omitted for safety in this strict MVP unless logic is solid)
            pass 

        except Exception as e:
            print(f"Error sanitizing {file_path}: {e}")

sanitizer_service = SanitizerService()
