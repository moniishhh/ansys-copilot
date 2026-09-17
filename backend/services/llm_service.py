"""LLM interaction layer using Azure AI Foundry via LangChain."""

from langchain_core.messages import HumanMessage

from langchain_openai import AzureChatOpenAI

from backend.config import settings


def create_chat_model() -> AzureChatOpenAI:
    """Create the Azure-hosted chat model shared by generation and RAG."""
    if not all((
        settings.azure_openai_api_key,
        settings.azure_openai_endpoint,
        settings.azure_openai_deployment,
    )):
        raise RuntimeError(
            "AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and "
            "AZURE_OPENAI_DEPLOYMENT must be configured."
        )

    return AzureChatOpenAI(
        azure_deployment=settings.azure_openai_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        # Azure reasoning models use their default temperature and the newer
        # max_completion_tokens request field.
        max_completion_tokens=settings.max_tokens,
    )


class LLMService:
    """Thin wrapper around the configured Azure AI Foundry deployment.

    Provides a simple ``generate`` interface used by other services.
    """

    def __init__(self) -> None:
        self._llm = create_chat_model()

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Send a prompt to the LLM and return the response text.

        Args:
            prompt: The user-facing prompt / question.
            system_prompt: Optional system-level instruction to prepend.

        Returns:
            The model's text response.
        """
        # Keep one unified prompt so all service paths behave consistently.
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        response = self._llm.invoke([HumanMessage(content=full_prompt)])
        return response.content
        
    def generate_structured(self, prompt: str, schema: type, system_prompt: str = ""):
        """Send a prompt to the LLM and return a parsed Pydantic object.

        Args:
            prompt: The user-facing prompt / question.
            schema: The Pydantic model class to parse into.
            system_prompt: Optional system-level instruction to prepend.

        Returns:
            An instance of the provided Pydantic schema.
        """
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
            
        structured_llm = self._llm.with_structured_output(schema)
        response = structured_llm.invoke([HumanMessage(content=full_prompt)])
        return response
