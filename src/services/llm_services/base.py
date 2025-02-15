from abc import ABC, abstractmethod
import logging
from typing import List
from langchain_core.tools import BaseTool

from src.core.llm_interface import LLMProvider


class LLMService(ABC):
    def __init__(self, llm_provider: type[LLMProvider], tools: List[BaseTool] = None):
        self.llm = llm_provider(tools=tools or [])
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def _get_system_message(self) -> str:
        """Returns the system message for the LLM"""
        pass

    @abstractmethod
    def _get_prompt(self, *args, **kwargs) -> str:
        """Returns the prompt for the LLM"""
        pass

    @abstractmethod
    def _parse_response(self, response: str):
        """Parses the LLM response"""
        pass

    def _execute(self, *args, system_message=True, **kwargs):
        """Execute the LLM tool with error handling"""
        try:
            prompt = self._get_prompt(*args, **kwargs)
            system_message = self._get_system_message() if system_message else None
            response = self.llm.generate_response(prompt, system_message)
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise 