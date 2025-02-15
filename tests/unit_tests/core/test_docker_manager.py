import pytest
from unittest.mock import Mock, patch
from src.core.docker_manager import DockerManager

class TestDockerManager:
    @pytest.fixture
    def mock_docker_client(self):
        return Mock()

    @pytest.fixture
    def docker_manager(self, mock_docker_client):
        with patch('docker.from_env', return_value=mock_docker_client):
            manager = DockerManager()
            return manager

    def test_build_image_success(self, docker_manager, mock_docker_client):
        # Setup
        dockerfile_path = "/path/to/dockerfile"
        tag = "test:latest"
        
        # Execute
        result = docker_manager.build_image(dockerfile_path, tag)
        
        # Verify
        assert result is True
        mock_docker_client.images.build.assert_called_once_with(
            path=str(dockerfile_path),
            tag=tag,
            rm=True
        )

    def test_build_image_failure(self, docker_manager, mock_docker_client):
        # Setup
        mock_docker_client.images.build.side_effect = Exception("Build failed")
        
        # Execute and verify
        with pytest.raises(Exception) as exc_info:
            docker_manager.build_image("/path/to/dockerfile", "test:latest")
        assert str(exc_info.value) == "Build failed"

    def test_test_container_success(self, docker_manager, mock_docker_client):
        # Setup
        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.return_value = b"Test logs"
        mock_docker_client.containers.run.return_value = mock_container
        
        # Execute
        result = docker_manager.test_container("test:latest", "python test.py")
        
        # Verify
        assert result is True
        mock_docker_client.containers.run.assert_called_once_with(
            "test:latest",
            command="python test.py",
            detach=True,
            stdout=True,
            stderr=True
        )

    def test_test_container_failure(self, docker_manager, mock_docker_client):
        # Setup
        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 1}
        mock_container.logs.return_value = b"Error logs"
        mock_docker_client.containers.run.return_value = mock_container
        
        # Execute
        result = docker_manager.test_container("test:latest", "python test.py")
        
        # Verify
        assert result is False 