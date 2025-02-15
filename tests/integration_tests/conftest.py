import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from tests.mocks.docker_mocks import MockDockerClient
from langchain_core.messages import AIMessage


@pytest.fixture
def setup_env(monkeypatch):
    # Mock environment
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")


@pytest.fixture
def should_docker_client_succeed():
    return True


@pytest.fixture
def mock_docker_client(should_docker_client_succeed):
    with patch('docker.from_env',
               return_value=MockDockerClient(should_succeed=should_docker_client_succeed)) as docker_client:
        yield docker_client


@pytest.fixture
def mock_llm_invoke():
    # Mock token usage metadata
    mock_usage = {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150
    }

    # Mock LLM responses
    mock_responses = {
        "analyze_script": AIMessage(
            content='{"language": "javascript", "version_requirements": {"node": ">= 14"}, "system_dependencies": [], "environment_variables": [], "execution_pattern": {"command": "node vowel_counter.js", "args": ["<input_text>"]}}',
            additional_kwargs={},
            usage_metadata=mock_usage
        ),
        "generate_dockerfile": AIMessage(
            content="""FROM node:14
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
CMD ["node", "vowel_counter.js"]""",
            additional_kwargs={},
            usage_metadata=mock_usage
        ),
        "analyze_example": AIMessage(
            content="node vowel_counter.js <input_text>",
            additional_kwargs={},
            usage_metadata=mock_usage
        )
    }

    def _mock_invoke(messages, config=None):
        # Determine which type of request this is based on the system message
        system_msg = messages["messages"][0].content if messages["messages"][0].content else ""
        if "system analyst" in system_msg and "script" in system_msg:
            return {"messages": [mock_responses["analyze_script"]]}
        elif "Docker container engineer" in system_msg:
            return {"messages": [mock_responses["generate_dockerfile"]]}
        elif "system analyst" in system_msg and "example" in system_msg:
            return {"messages": [mock_responses["analyze_example"]]}
        return {"messages": [AIMessage(content="default response", additional_kwargs={}, usage_metadata=mock_usage)]}

    # Create a mock agent
    mock_agent = MagicMock()
    mock_agent.invoke.side_effect = _mock_invoke

    # Patch the create_react_agent to return the mock agent
    with patch('src.core.llm_interface.create_react_agent', return_value=mock_agent):
        yield mock_agent


def get_example_scripts():
    # Get all scripts from examples directory
    current_dir = Path(__file__).parent
    examples_dir = current_dir.parent.parent / "examples" / "sample_scripts"
    if not examples_dir.exists():
        raise FileNotFoundError(f"Examples directory not found at {examples_dir}")

    scripts = []
    for script_path in examples_dir.glob("*.*"):
        if script_path.name.startswith("README_"):
            continue
        # Find corresponding README for each script
        readme_path = examples_dir / f"README_{script_path.stem}.md"
        if readme_path.exists():
            scripts.append((str(script_path), str(readme_path)))

    if not scripts:
        raise FileNotFoundError(
            "No example scripts found in examples/sample_scripts/. Please add sample scripts with corresponding README_*.md files")

    return scripts


@pytest.fixture(params=get_example_scripts())
def script_example_paths(request):
    return request.param


@pytest.fixture(params=["openai", "google"])
def model(request):
    return request.param


@pytest.fixture(autouse=True)
def integration_mocks(setup_env, mock_docker_client, mock_llm_invoke):
    pass