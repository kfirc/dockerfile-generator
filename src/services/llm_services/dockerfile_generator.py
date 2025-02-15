from src.core.llm_interface import LLMProvider
from src.services.llm_services.base import LLMService
from src.models.docker_file_generation import DockerfileGenerationRequest
from src.constants import PromptConstants, MAX_GENERATION_ATTEMPTS
import os

from src.services.tool_services.build_image import BuildImageTool
from src.services.tool_services.test_container import TestContainerTool


class DockerfileGenerator(LLMService):
    def __init__(
            self,
            llm_provider: type[LLMProvider],
            build_image_tool: BuildImageTool,
            test_container_tool: TestContainerTool,
    ):
        self.build_image_tool = build_image_tool
        self.test_container_tool = test_container_tool
        self.max_attempts = MAX_GENERATION_ATTEMPTS  # Set the maximum attempts
        super().__init__(llm_provider, tools=[build_image_tool, test_container_tool])

    def _get_system_message(self) -> str:
        return PromptConstants.SYSTEM_MESSAGE_DOCKERFILE_GENERATOR

    def _get_prompt(
            self,
            script_analysis: DockerfileGenerationRequest,
            script_name: str,
            test_command: str,
            error=None,
            *_, **__,
    ) -> str:
        if error:
            return PromptConstants.PROMPT_DOCKERFILE_ERROR.format(error=error)

        script_filename = os.path.basename(script_name)
        return PromptConstants.PROMPT_DOCKERFILE_GENERATOR.format(
            requirements=script_analysis.model_dump_json(),
            script_filename=script_filename,
            command=test_command,
        )

    def _parse_response(self, response: str) -> str:
        """Clean excess markdown from the response"""
        cleaned_response = response.strip('```dockerfile\n').strip('```').strip()
        return cleaned_response

    def generate_dockerfile(self, request: DockerfileGenerationRequest) -> DockerfileGenerationRequest:
        first_run = True
        error = False
        dockerfile_content = None
        attempts = 0  # Initialize attempt counter

        while (first_run or error) and attempts < self.max_attempts:
            dockerfile_content = self._execute(
                script_analysis=request.script_analysis,
                script_name=request.build_context.script_name,
                test_command=request.test_command,
                error=error,
                system_message=first_run,
            )

            first_run = False
            error = self.build_image_tool._run(dockerfile_content)

            if not error:
                error = self.test_container_tool._run()

            attempts += 1  # Increment the attempt counter

        request.file_content = dockerfile_content
        return request
