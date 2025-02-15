from pydantic import BaseModel
from typing import List


class ScriptAnalysis(BaseModel):
    language: str
    version_requirements: dict
    system_dependencies: List[str]
    environment_variables: List[str]
    execution_pattern: dict
