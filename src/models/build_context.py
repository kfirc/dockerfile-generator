from pydantic import BaseModel
from typing import Optional
import os
import shutil

class BuildContext(BaseModel):
    script_name: str
    script_path: str
    context_root: str = "build_context"
    
    def get_context_directory(self) -> str:
        """Get the directory path for this build context"""
        return os.path.join(self.context_root, self.script_name)
    
    def get_dockerfile_path(self) -> str:
        """Get the full path for the Dockerfile"""
        return os.path.join(self.get_context_directory(), "Dockerfile")
    
    def get_script_destination(self) -> str:
        """Get the destination path for the script"""
        return os.path.join(self.get_context_directory(), os.path.basename(self.script_path))

    def get_image_tag(self) -> str:
        return f"script-container:{self.script_name}"
