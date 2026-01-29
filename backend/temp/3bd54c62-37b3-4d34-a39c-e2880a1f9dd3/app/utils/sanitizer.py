import re
import os
import shutil
import logging
from typing import Set

logger = logging.getLogger(__name__)

class SanitizerService:
    # Regex patterns for detecting PII and secrets
    PATTERNS = {
        # API Keys and Tokens
        'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
        'secret_key': r'(?i)(secret[_-]?key|secret)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
        'token': r'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']?([a-zA-Z0-9_\-\.]{20,})["\']?',
        
        # AWS Credentials
        'aws_access_key': r'(?i)(AKIA[0-9A-Z]{16})',
        'aws_secret': r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?',
        
        # Database URLs and passwords
        'db_password': r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^\s\'"]+)["\']?',
        'connection_string': r'(?i)(mongodb|mysql|postgresql|postgres|sql)://[^\s]+',
        
        # Private Keys
        'private_key_marker': r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE\s*KEY',
        'private_key_content': r'-----BEGIN[^-]*PRIVATE[^-]*-----[\s\S]*?-----END[^-]*PRIVATE[^-]*-----',
        
        # Email addresses (basic)
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        
        # URLs with credentials
        'url_with_creds': r'(http|https|ftp)://[a-zA-Z0-9:_\-\.]+@',
        
        # Potential hardcoded passwords (common patterns)
        'hardcoded_password': r'(?i)(password\s*=|pwd\s*=|passwd\s*=)\s*["\']([^\'"]+)["\']',
        
        # Google API Keys
        'google_api_key': r'AIza[0-9A-Za-z\-_]{35}',
        
        # Stripe keys
        'stripe_key': r'(sk|pk)_(live|test)_[0-9a-zA-Z]{24,}',
    }

    # File extensions to scan
    TEXT_EXTENSIONS = ('.py', '.txt', '.md', '.json', '.yml', '.yaml', '.ini', '.cfg', '.toml', '.env', '.sh', '.bash', '.js', '.ts')
    
    # Files/directories to delete entirely
    DANGEROUS_FILES = {'.env', '.env.local', '.env.*.local'}
    DANGEROUS_DIRS = {'.git', '.aws', '.gcp', 'venv', 'env', '__pycache__', 'node_modules'}

    @staticmethod
    def sanitize_directory(directory_path: str) -> dict:
        """
        Recursively walks through a directory and sanitizes PII/Secrets.
        
        Returns:
            dict: Statistics about sanitization (files_removed, files_sanitized, issues_found)
        """
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        logger.info(f"Starting sanitization of: {directory_path}")
        
        stats = {
            'files_removed': 0,
            'files_sanitized': 0,
            'issues_found': []
        }
        
        # Walk through directory
        for root, dirs, files in os.walk(directory_path, topdown=True):
            # Remove dangerous directories
            for danger_dir in list(dirs):
                if danger_dir in SanitizerService.DANGEROUS_DIRS:
                    dir_path = os.path.join(root, danger_dir)
                    try:
                        shutil.rmtree(dir_path)
                        logger.info(f"Removed dangerous directory: {dir_path}")
                        stats['files_removed'] += 1
                    except Exception as e:
                        logger.error(f"Failed to remove directory {dir_path}: {e}")
                        stats['issues_found'].append(f"Failed to remove {dir_path}: {e}")
            
            # Remove dangerous directories from traversal
            dirs[:] = [d for d in dirs if d not in SanitizerService.DANGEROUS_DIRS]
            
            # Process files
            for file in files:
                file_path = os.path.join(root, file)
                
                # Delete dangerous files
                if file in SanitizerService.DANGEROUS_FILES or any(
                    file.endswith(ext) and 'secret' in file.lower() or 'key' in file.lower()
                    for ext in ('.pem', '.key', '.crt', '.p12', '.pfx')
                ):
                    try:
                        os.remove(file_path)
                        logger.info(f"Removed dangerous file: {file_path}")
                        stats['files_removed'] += 1
                    except Exception as e:
                        logger.error(f"Failed to remove file {file_path}: {e}")
                        stats['issues_found'].append(f"Failed to remove {file_path}: {e}")
                    continue
                
                # Scan and scrub text files
                if any(file.endswith(ext) for ext in SanitizerService.TEXT_EXTENSIONS):
                    try:
                        was_modified = SanitizerService._scrub_file(file_path)
                        if was_modified:
                            stats['files_sanitized'] += 1
                    except Exception as e:
                        logger.error(f"Error sanitizing {file_path}: {e}")
                        stats['issues_found'].append(f"Failed to sanitize {file_path}: {e}")
        
        logger.info(f"Sanitization complete. Removed: {stats['files_removed']}, "
                   f"Sanitized: {stats['files_sanitized']}, Issues: {len(stats['issues_found'])}")
        return stats

    @staticmethod
    def _scrub_file(file_path: str) -> bool:
        """
        Reads a file, redacts secrets, and writes back if modified.
        
        Returns:
            bool: True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
            
            content = original_content
            modified = False
            redactions = []
            
            # Apply all patterns
            for pattern_name, pattern in SanitizerService.PATTERNS.items():
                # Find all matches before replacing
                matches = list(re.finditer(pattern, content))
                if matches:
                    for match in matches:
                        redactions.append(pattern_name)
                        logger.debug(f"Found {pattern_name} in {file_path}: {match.group(0)[:50]}...")
                    
                    # Replace matched content
                    content = re.sub(pattern, r'[REDACTED]', content)
                    modified = True
            
            # Write back if modified
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Log unique redactions
                unique_redactions = set(redactions)
                logger.info(f"Sanitized {file_path}: redacted {len(redactions)} items "
                           f"({', '.join(unique_redactions)})")
            
            return modified
        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            raise

sanitizer_service = SanitizerService()
