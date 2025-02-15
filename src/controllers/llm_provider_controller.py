from src.constants import VALID_VENDORS, ValidVendorArgument
from src.core.llm_interface import LLMProvider, GoogleGenerativeAIProvider, OpenAIProvider
from src.services.security_service import SecurityService


class LLMProviderController:
    def __init__(self, model: ValidVendorArgument):
        self.security_service = SecurityService()
        self.model = model

    def get_llm_provider(self) -> type[LLMProvider]:
        """
        Factory function to return a class of an LLMProvider based on the vendor.

        Returns:
            type[LLMProvider]: A class of a concrete LLMProvider.
        """
        if not self.security_service.sanitize_model_name(self.model):
            raise ValueError("Invalid model name")

        vendor = self.model.lower()
        if vendor == VALID_VENDORS[0]:
            return OpenAIProvider
        elif vendor == VALID_VENDORS[1]:
            return GoogleGenerativeAIProvider
        else:
            raise ValueError(f"Unsupported LLM vendor: {vendor}")
