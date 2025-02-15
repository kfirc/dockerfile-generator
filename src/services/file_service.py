from src.core.file_interface import FileInterface
from src.models.build_context import BuildContext
from src.models.docker_file_generation import DockerfileGenerationRequest


class FileService:
    def __init__(self):
        self.file_interface = FileInterface()

    def prepare_build_context(self, build_context: BuildContext):
        """Prepare the build context directory and copy the script."""
        self.file_interface.create_directory_if_not_exists(build_context.get_context_directory())
        self.file_interface.copy_file(build_context.script_path, build_context.get_script_destination())

    def save_dockerfile(self, request: DockerfileGenerationRequest) -> str:
        """Ensure that the build context is prepared and save the Dockerfile."""
        self.prepare_build_context(request.build_context)
        dockerfile_path = request.build_context.get_dockerfile_path()
        self.file_interface.write_file(dockerfile_path, request.file_content)
        return dockerfile_path
