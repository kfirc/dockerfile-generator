import logging
from typing import Optional, Type
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from src.core.docker_manager import DockerManager
from src.core.file_interface import FileInterface
from src.models.tool_input import BuildInput


logger = logging.getLogger(__name__)


class BuildImageTool(BaseTool):
    name: str = "build_image"
    description: str = (
        "Build a Docker image from a Dockerfile. This tool saves the provided Dockerfile content to a specified file "
        "and attempts to build the Docker image using Docker's build command. If the build fails, the full error message "
        "from Docker's build process is returned, allowing for inspection and modification of the Dockerfile to resolve "
        "the issue. If the build succeeds, nothing will be returned."
    )
    args_schema: Type[BaseModel] = BuildInput

    class Config:
      extra = "allow"

    def __init__(self, docker_manager: DockerManager, file_interface: FileInterface, dockerfile_path: str, tag: str):
        super().__init__()
        self.docker_manager = docker_manager
        self.file_interface = file_interface
        self.dockerfile_path = dockerfile_path
        self.tag = tag
        self.logger = logging.getLogger(__name__)

    def _run(self, dockerfile_content: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Optional[str]:
        """
        Save the dockerfile and build the image

        :param dockerfile_content: The content of the Dockerfile
        :param run_manager: The run manager
        :return: None if the build was successful, otherwise the error message
        """
        self.logger.info(f"Trying to build Docker image with tag: {self.tag}")
        self.logger.debug(f"Dockerfile content: {dockerfile_content}")
        self.file_interface.write_file(self.dockerfile_path, dockerfile_content)
        directory = self.file_interface.get_directory(self.dockerfile_path)

        try:
            self.docker_manager.build_image(directory, self.tag)
            return None
        except Exception as e:
            return str(e)
