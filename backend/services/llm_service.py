"""LLM interaction layer using Google Gemini via LangChain."""

from langchain_core.messages import HumanMessage

from langchain_google_genai import ChatGoogleGenerativeAI

from backend.config import settings


class LLMService:
    """Thin wrapper around LangChain's ChatGoogleGenerativeAI client.

    Provides a simple ``generate`` interface used by other services.
    """

    def __init__(self) -> None:
        self._llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            temperature=settings.temperature,
            max_output_tokens=settings.max_tokens,
            google_api_key=settings.gemini_api_key,
        )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Send a prompt to the LLM and return the response text.

        Args:
            prompt: The user-facing prompt / question.
            system_prompt: Optional system-level instruction to prepend.

        Returns:
            The model's text response.
        """
        # Gemini works best with a single unified prompt;
        # prepend any system instruction directly into the message.
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        response = self._llm.invoke([HumanMessage(content=full_prompt)])
        return response.content
