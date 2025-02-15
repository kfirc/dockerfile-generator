from pydantic import BaseModel
from typing import List, Optional
import os
from src.models.script_analysis import ScriptAnalysis
from src.models.build_context import BuildContext


class DockerfileGenerationRequest(BaseModel):
    script_analysis: ScriptAnalysis
    test_command: str
    build_context: BuildContext
    file_content: Optional[str] = None

    def get_save_directory(self) -> str:
        """Determine the directory to save the Dockerfile."""
        if self.build_context.context_root:
            return self.build_context.context_root
        else:
            # Create a new folder in the repo if no custom folder is provided
            return os.path.join(os.path.dirname(self.script_analysis.script_path), "dockerfiles")
