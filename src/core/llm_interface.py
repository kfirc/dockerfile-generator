import os
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import uuid
from langgraph.prebuilt import create_react_agent, ToolExecutor
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

from src.constants import LLMProviderConstants, TokenUsageConstants, VALID_VENDORS, ValidVendorArgument


class LLMProvider(ABC):
    def __init__(self, model_name: str = None, temperature: float = None, tools: Optional[List] = None, thread_id: Optional[str] = None):
        self.token_usage = TokenUsageConstants.DEFAULT_TOKEN_USAGE.copy()
        self.tools = tools or []
        self.thread_id = thread_id or str(uuid.uuid4())
        self.llm = self.initialize_llm(model_name, temperature)
        self.checkpointer = MemorySaver()
        self.tool_executor = ToolExecutor(self.tools)

        # Read the DEBUG_MODE environment variable
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tool_executor,
            checkpointer=self.checkpointer,
            debug=self.debug_mode,
        )

    @property
    def debug_mode(self):
        return os.getenv("DEBUG_MODE", "False").lower() == "true"

    @abstractmethod
    def initialize_llm(self, model_name: str, temperature: float):
        """Initialize the LLM instance."""
        pass

    def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Generate a response using the LLM."""
        messages = self._construct_messages(prompt, system_message)
        config = {"configurable": {"thread_id": self.thread_id}}
        response = self.agent.invoke({"messages": messages}, config=config)
        ai_message = response["messages"][-1]

        # Extract token usage
        token_usage = ai_message.usage_metadata
        self.token_usage = {
            "input_tokens": token_usage["input_tokens"],
            "output_tokens": token_usage["output_tokens"],
            "total_tokens": token_usage["total_tokens"],
        }

        return ai_message.content

    def _construct_messages(self, prompt: str, system_message: Optional[str]) -> list:
        """Construct messages for LLM invocation."""
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))
        return messages

    def get_token_usage(self) -> Dict[str, int]:
        """Retrieve token usage data."""
        return self.token_usage


class GoogleGenerativeAIProvider(LLMProvider):
    def initialize_llm(self, model_name: str = None, temperature: float = None):
        return ChatGoogleGenerativeAI(
            model=model_name or LLMProviderConstants.DEFAULT_GOOGLE_MODEL_NAME,
            temperature=temperature or LLMProviderConstants.DEFAULT_GOOGLE_TEMPERATURE,
        )


class OpenAIProvider(LLMProvider):
    def initialize_llm(self, model_name: str = None, temperature: float = None):
        return ChatOpenAI(
            model_name=model_name or LLMProviderConstants.DEFAULT_OPENAI_MODEL_NAME,
            temperature=temperature or LLMProviderConstants.DEFAULT_OPENAI_TEMPERATURE,
        )
