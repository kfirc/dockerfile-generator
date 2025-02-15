import os
import logging

from src.models.script_analysis import ScriptAnalysis
from src.services.file_service import FileService
from src.services.llm_services.script_analyzer import ScriptAnalyzer
from src.services.llm_services.dockerfile_generator import DockerfileGenerator
from src.services.llm_services.example_analyzer import ExampleAnalyzer
from src.core.docker_manager import DockerManager
from src.models.docker_file_generation import DockerfileGenerationRequest
from src.models.build_context import BuildContext
from src.services.tool_services.build_image import BuildImageTool
from src.services.tool_services.test_container import TestContainerTool
from src.services.security_service import SecurityService


class ImageGenerationController:
    def __init__(self, llm_provider):
        self.logger = logging.getLogger(__name__)
        self.llm_provider = llm_provider
        self.script_analyzer = ScriptAnalyzer(self.llm_provider)
        self.example_analyzer = ExampleAnalyzer(self.llm_provider)
        self.docker_manager = DockerManager()
        self.file_service = FileService()
        self.security_service = SecurityService()

    def run(self, script_path: str, example_path: str) -> bool:
        try:
            script_path, example_path = self.security_service.sanitize_paths(script_path, example_path)

            self.logger.info("Analyzing script...")
            analysis = self.script_analyzer.analyze_script(script_path)

            self.logger.info("Analyzing example file...")
            test_command = self.generate_test_command(example_path)

            self.logger.info("Creating build context...")
            script_name = os.path.splitext(os.path.basename(script_path))[0]
            build_context = BuildContext(script_name=script_name, script_path=script_path)
            tag = build_context.get_image_tag()

            self.file_service.prepare_build_context(build_context)

            self.logger.info("Generating Dockerfile...")
            self.generate_dockerfile(build_context, analysis, test_command)

            self.logger.info("Building Docker image...")
            self.logger.info(f"Image tag: {tag}")
            self.docker_manager.build_image(build_context.get_context_directory(), tag)

            self.logger.info("Testing Docker container...")
            tested_successfully = self.docker_manager.test_container(tag, test_command)

            if not tested_successfully:
                self.logger.error("Container test failed!")
                return False

            self.logger.info("Container tested successfully!")
            return True
                
        except Exception as e:
            self.logger.exception(f"Error in orchestration process")
            return False

    def generate_dockerfile(self, build_context: BuildContext, analysis: ScriptAnalysis, test_command: str):
        build_image_tool = BuildImageTool(
            docker_manager=self.docker_manager,
            file_interface=self.file_service.file_interface,
            dockerfile_path=build_context.get_dockerfile_path(),
            tag=build_context.get_image_tag(),
        )

        test_container_tool = TestContainerTool(
            docker_manager=self.docker_manager,
            tag=build_context.get_image_tag(),
            test_command=test_command,
        )

        dockerfile_request = DockerfileGenerationRequest(
            script_analysis=analysis,
            test_command=test_command,
            build_context=build_context,
        )

        dockerfile_generator = DockerfileGenerator(
            llm_provider=self.llm_provider,
            build_image_tool=build_image_tool,
            test_container_tool=test_container_tool,
        )

        dockerfile_request = dockerfile_generator.generate_dockerfile(dockerfile_request)
        self.file_service.save_dockerfile(dockerfile_request)

    def generate_test_command(self, example_path: str) -> str:
        test_command = self.example_analyzer.analyze_example(example_path)
        sanitized_command = self.security_service.sanitize_test_command(test_command)
        if not sanitized_command:
            raise ValueError("Invalid test command")
        return sanitized_command
