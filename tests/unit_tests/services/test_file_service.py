import pytest
from unittest.mock import Mock

from src.models.script_analysis import ScriptAnalysis
from src.services.file_service import FileService
from src.models.build_context import BuildContext
from src.models.docker_file_generation import DockerfileGenerationRequest

class TestFileService:
    @pytest.fixture
    def mock_file_interface(self):
        return Mock()

    @pytest.fixture
    def script_analysis(self):
        return ScriptAnalysis(
            language="python",
            version_requirements={"python": ">=3.6"},
            system_dependencies=[],
            environment_variables=[],
            execution_pattern={
                "command": "python script.py",
                "args": ["<input>"]
            }
        )

    @pytest.fixture
    def file_service(self, mock_file_interface):
        service = FileService()
        service.file_interface = mock_file_interface
        return service

    def test_prepare_build_context(self, file_service, mock_file_interface):
        # Setup
        build_context = BuildContext(
            script_name="test_script",
            script_path="/path/to/script.py"
        )

        # Execute
        file_service.prepare_build_context(build_context)

        # Verify
        mock_file_interface.create_directory_if_not_exists.assert_called_once_with(
            build_context.get_context_directory()
        )
        mock_file_interface.copy_file.assert_called_once_with(
            build_context.script_path,
            build_context.get_script_destination()
        )

    def test_save_dockerfile(self, file_service, mock_file_interface, script_analysis):
        # Setup
        build_context = BuildContext(
            script_name="test_script",
            script_path="/path/to/script.py"
        )
        request = DockerfileGenerationRequest(
            script_analysis=script_analysis,
            test_command="python test.py",
            build_context=build_context,
            file_content="FROM python:3.9"
        )

        # Execute
        result = file_service.save_dockerfile(request)

        # Verify
        mock_file_interface.write_file.assert_called_once_with(
            build_context.get_dockerfile_path(),
            request.file_content
        )
        assert result == build_context.get_dockerfile_path() 