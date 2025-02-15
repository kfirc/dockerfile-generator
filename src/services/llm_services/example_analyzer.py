from .base import LLMService
from src.constants import PromptConstants

class ExampleAnalyzer(LLMService):
    def _get_system_message(self) -> str:
        return PromptConstants.SYSTEM_MESSAGE_EXAMPLE_ANALYZER

    def _get_prompt(self, example_content: str, *_, **__) -> str:
        return PromptConstants.PROMPT_EXAMPLE_ANALYZER.format(example_content=example_content)

    def _parse_response(self, response: str) -> str:
        command = response.strip('`').strip()
        command = command.replace('bash', '').replace('shell', '').strip()
        command = command.strip()
        
        if not command:
            self.logger.error("No valid command found in example")
            raise ValueError("No valid command found in example")
            
        return command

    def analyze_example(self, example_path: str) -> str:
        with open(example_path, 'r') as file:
            example_content = file.read()
        return self._execute(example_content) 