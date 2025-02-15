import pytest
from src.services.llm_services.script_analyzer import ScriptAnalyzer
from src.models.script_analysis import ScriptAnalysis


class MockLLMProvider:
    def __init__(self, tools):
        self.tools = tools

    def generate_response(self, prompt, system_message=None):
        return (
            '{"language": "python",'
            '"version_requirements": {"python": ">=3.6"},'
            '"system_dependencies": [],'
            '"environment_variables": [],'
            '"execution_pattern": {'
            '"command": "python script.py",'
            '"args": ["<input>"]'
            '}}'
        )

class TestScriptAnalyzer:
    @pytest.fixture
    def mock_llm_provider(self):
        return MockLLMProvider  # Return an instance of the mock class

    def test_analyze_script(self, mock_llm_provider, tmp_path):
        # Setup
        analyzer = ScriptAnalyzer(mock_llm_provider)
        test_script = tmp_path / "test.py"
        test_script.write_text("print('Hello, World!')")

        # Execute
        result = analyzer.analyze_script(str(test_script))

        # Verify
        assert isinstance(result, ScriptAnalysis)
        assert result.language == "python"
        assert result.version_requirements == {"python": ">=3.6"}
        assert result.system_dependencies == []
        assert result.environment_variables == [] 