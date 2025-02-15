import logging
from typing import Optional
import re
import os
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class SecurityService:
    # Allowed file extensions for scripts
    ALLOWED_EXTENSIONS = {'.py', '.js', '.rb', '.sh', '.php', '.pl', '.java', '.go', '.md'}
    # Allowed models
    ALLOWED_MODELS = {'openai', 'google'}
    # Maximum file size (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    # Prompt injection patterns
    INJECTION_PATTERNS = (
        r'ignore previous instructions',
        r'disregard (all|previous)',
        r'system message:',
        r'you are not',
        r'new role:',
        r'<\/?system>',
        r'<\/?human>',
        r'<\/?assistant>'
    )

    def sanitize_path(self, file_path: str) -> Optional[str]:
        """Sanitize and validate file path"""
        try:
            # Convert to absolute path and resolve any symlinks
            abs_path = os.path.abspath(os.path.realpath(file_path))
            # Check if file exists and is a regular file
            if not os.path.isfile(abs_path):
                logger.warning(f"File not found: {abs_path}")
                return None
            # Check file extension
            if Path(abs_path).suffix not in self.ALLOWED_EXTENSIONS:
                logger.warning(f"Invalid file extension for: {abs_path}")
                return None
            # Check file size
            if os.path.getsize(abs_path) > self.MAX_FILE_SIZE:
                logger.warning(f"File size exceeds limit: {abs_path}")
                return None
            logger.info(f"Sanitized path: {abs_path}")
            return abs_path
        except (OSError, ValueError) as e:
            logger.error(f"Error sanitizing path: {e}")
            return None

    def sanitize_paths(self, script_path: str, example_path: str) -> Optional[tuple]:
        # Sanitize inputs
        script_path = self.sanitize_path(script_path)
        example_path = self.sanitize_path(example_path)

        if not script_path or not example_path:
            raise FileNotFoundError("Invalid input files")

        # Read and check for prompt injection
        with open(script_path, 'r') as f:
            script_content = f.read()
        with open(example_path, 'r') as f:
            example_content = f.read()

        if self.detect_prompt_injection(script_content) or \
                self.detect_prompt_injection(example_content):
            raise ValueError("Potential prompt injection detected")

        return script_path, example_path

    def sanitize_model_name(self, model: str) -> Optional[str]:
        """Sanitize and validate model name"""
        model = model.lower().strip()
        if model in self.ALLOWED_MODELS:
            logger.info(f"Sanitized model name: {model}")
            return model
        logger.warning(f"Invalid model name: {model}")
        return None

    def sanitize_test_command(self, command: str) -> Optional[str]:
        """Sanitize test command to prevent command injection"""
        # Remove any shell special characters and operators
        dangerous_patterns = r'[;&|`$]|\.\./'
        if re.search(dangerous_patterns, command):
            logger.warning(f"Potential command injection detected in command: {command}")
            return None
        logger.info(f"Sanitized test command: {command}")
        return command

    def detect_prompt_injection(self, content: str) -> bool:
        """Detect potential prompt injection attempts"""

        
        pattern = '|'.join(self.INJECTION_PATTERNS)
        if re.search(pattern, content, re.IGNORECASE):
            logger.warning("Potential prompt injection detected.")
            return True
        logger.info("No prompt injection detected.")
        return False 