import pytest
import sys
from unittest.mock import patch
from assertpy import assert_that
from main import main
from tests.integration_tests.conftest import get_example_scripts


@pytest.mark.integration
class TestIntegration:
    def test_main_workflow(self, script_example_paths, model, monkeypatch):
        script_path, example_path = script_example_paths
        test_args = ['main.py', script_path, example_path, '--model', model]
        monkeypatch.setattr(sys, 'argv', test_args)

        try:
            main()
            assert_that(False).is_true()
        except SystemExit as e:
            assert_that(e.code).is_equal_to(0)

    @pytest.mark.parametrize("script_example_paths", [("nonexistent_script.py", "example.md")])
    def test_main_with_nonexistent_script_should_fail(self, script_example_paths, monkeypatch):
        script_path, example_path = script_example_paths
        test_args = ['main.py', script_path, example_path]
        monkeypatch.setattr(sys, 'argv', test_args)

        try:
            main()
        except SystemExit as e:
            assert_that(e.code).is_equal_to(1)

    @pytest.mark.parametrize("should_docker_client_succeed", [False])
    def test_main_with_docker_failure_should_fail(self, script_example_paths, monkeypatch):
        script_path, example_path = script_example_paths
        test_args = ['main.py', script_path, example_path]
        monkeypatch.setattr(sys, 'argv', test_args)

        try:
            main()
        except SystemExit as e:
            assert_that(e.code).is_equal_to(1)

    def test_dockerfile_creation_in_build_context(self, script_example_paths, monkeypatch, tmp_path, model):
        script_path, example_path = script_example_paths
        test_args = ['main.py', script_path, example_path, '--model', model]
        monkeypatch.setattr(sys, 'argv', test_args)

        # Create a temporary build context directory
        build_context_dir = tmp_path / "build_context"
        build_context_dir.mkdir()

        # Mock the build_context to point to the temporary directory
        with patch('src.models.build_context.BuildContext.get_dockerfile_path', return_value=str(build_context_dir / "Dockerfile")), \
             patch('src.models.build_context.BuildContext.get_image_tag', return_value="test_image"):
            try:
                main()
                dockerfile_path = build_context_dir / "Dockerfile"
                assert_that(dockerfile_path.exists()).is_true()
            except SystemExit as e:
                assert_that(e.code).is_equal_to(0)

    @pytest.mark.parametrize("script_example_paths", get_example_scripts()[:1])
    def test_docker_build_command_called(self, script_example_paths, monkeypatch, model, mock_docker_client):
        script_path, example_path = script_example_paths
        test_args = ['main.py', script_path, example_path, '--model', model]
        monkeypatch.setattr(sys, 'argv', test_args)

        try:
            main()
        except SystemExit as e:
            assert_that(e.code).is_equal_to(0)

        mock_docker_client_instance = mock_docker_client()
        assert_that(mock_docker_client_instance.images.build.called).is_true()
        mock_docker_client_instance.images.build.assert_called_with(
            path="build_context/char_counter",
            tag="script-container:char_counter",
            rm=True
        )
