"""Application settings loaded from environment variables via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for ANSYS Copilot backend."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM settings
    openai_api_key: str = ""
    model_name: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 4096

    # Embedding & vector store settings
    embedding_model: str = "text-embedding-3-small"
    chroma_persist_dir: str = "./chroma_db"


# Global settings instance used throughout the application
settings = Settings()
