import docker
import logging


class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.logger = logging.getLogger(__name__)
        self.run_history = []

    def build_image(self, dockerfile_path: str, tag: str) -> bool:
        try:
            self.client.images.build(
                path=str(dockerfile_path),
                tag=tag,
                rm=True
            )
            self.logger.info(f"Docker image built successfully with tag: {tag}")
            return True
        except Exception as e:
            self.logger.error(f"Error building Docker image: {e}")
            raise

    def test_container(self, tag: str, test_command: str) -> bool:
        self.logger.info(f"Test command: {test_command}")
        container = None

        try:
            # Run container and capture output
            container = self.client.containers.run(
                tag,
                command=test_command,
                detach=True,
                stdout=True,  # Capture stdout
                stderr=True  # Capture stderr
            )

            # Wait for the container to finish
            result = container.wait()
            exit_code = result["StatusCode"]
            logs = container.logs().decode("utf-8")
            self.logger.info(f"Container logs: {logs}")
            self.logger.debug(f"Container exited with code: {exit_code}")

            self.run_history.append({
                "tag": tag,
                "test_command": test_command,
                "exit_code": exit_code,
                "logs": logs
            })

            return exit_code == 0

        except Exception as e:
            self.logger.error(f"Error testing container: {e}")
            raise

        finally:
            # Ensure the container is removed, even if an exception occurs
            try:
                container.remove(force=True)
            except Exception as cleanup_error:
                self.logger.warning(f"Failed to remove container: {cleanup_error}")

