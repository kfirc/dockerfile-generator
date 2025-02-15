from unittest.mock import MagicMock

class MockContainer:
    def __init__(self, exit_code=0):
        self.exit_code = exit_code
        self.attrs = {'State': {'ExitCode': exit_code}}
    
    def wait(self):
        return {'StatusCode': self.exit_code}
    
    def logs(self):
        return b"Mock container logs"
    
    def remove(self):
        pass

    def remove(self, force=False):
        pass


class MockImageBuilder:
    def build(self, **kwargs):
        return [{'stream': 'Step 1/5: Mock build step'}]

class MockDockerClient:
    def __init__(self, should_succeed=True):
        self.images = MagicMock()
        self.containers = MagicMock()
        self.should_succeed = should_succeed
        
        # Setup image building
        self.images.build.return_value = MockImageBuilder().build()
        
        # Setup container running
        container = MockContainer(exit_code=0 if should_succeed else 1)
        self.containers.run.return_value = container 