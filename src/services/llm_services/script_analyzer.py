from src.services.llm_services.base import LLMService
from src.models.script_analysis import ScriptAnalysis
from src.constants import PromptConstants


class ScriptAnalyzer(LLMService):
    def _get_system_message(self) -> str:
        return PromptConstants.SYSTEM_MESSAGE_SCRIPT_ANALYZER

    def _get_prompt(self, script_content: str, *_, **__) -> str:
        return PromptConstants.PROMPT_SCRIPT_ANALYZER.format(script_content=script_content)

    def _parse_response(self, response: str) -> ScriptAnalysis:
        # Clean the response to remove any Markdown formatting
        cleaned_response = response.strip('```json\n').strip('```').strip()
        return ScriptAnalysis.model_validate_json(cleaned_response)

    def analyze_script(self, script_path: str) -> ScriptAnalysis:
        with open(script_path, 'r') as file:
            script_content = file.read()
        return self._execute(script_content)
