"""Application settings loaded from environment variables via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for ANSYS Copilot backend."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Azure AI Foundry / Azure OpenAI settings
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_deployment: str = "gpt-5.4"
    max_tokens: int = 4096

    # Embedding & vector store settings
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_persist_dir: str = "./chroma_db"


# Global settings instance used throughout the application
settings = Settings()
