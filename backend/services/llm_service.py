"""LLM interaction layer supporting OpenAI-compatible models."""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from backend.config import settings


class LLMService:
    """Thin wrapper around LangChain's ChatOpenAI client.

    Provides a simple ``generate`` interface used by other services.
    """

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Send a prompt to the LLM and return the response text.

        Args:
            prompt: The user-facing prompt / question.
            system_prompt: Optional system-level instruction to prepend.

        Returns:
            The model's text response.
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        response = self._llm.invoke(messages)
        return response.content
