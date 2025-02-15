import logging
from typing import Optional, Type
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from src.core.docker_manager import DockerManager
from src.models.tool_input import TestContainerInput


logger = logging.getLogger(__name__)


class TestContainerTool(BaseTool):
    name: str = "test_container"
    description: str = (
        "Test a Docker container by running a specified command. If the container runs successfully, "
        "nothing will be returned. If it fails, the full error message from Docker's process will be returned, "
        "allowing for inspection and modification of the container or command to resolve the issue."
    )
    args_schema: Type[BaseModel] = TestContainerInput

    class Config:
        extra = "allow"

    def __init__(self, docker_manager: DockerManager, tag: str, test_command: str):
        super().__init__()
        self.docker_manager = docker_manager
        self.tag = tag
        self.test_command = test_command
        self.logger = logging.getLogger(__name__)

    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> Optional[str]:
        """
        Run a test command inside the Docker container.

        :param run_manager: The run manager
        :return: None if the test was successful, otherwise the error message
        """
        self.logger.info(f"Testing Docker container with tag: {self.tag}")

        try:
            success = self.docker_manager.test_container(self.tag, self.test_command)
            run_logs = self.docker_manager.run_history[-1]
            return None if success else f"Container test failed. Logs: {run_logs}"
        except Exception as e:
            self.logger.warning(f"Error testing Docker container: {e}")
            return str(e)
