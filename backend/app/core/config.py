# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Artha Sutra API"
    ENVIRONMENT: str = "development"

    # API Keys
    TAVILY_API_KEY: str
    OPENAI_API_KEY: str
    KITE_API_KEY: str
    KITE_API_SECRET: str

    # Database URLs
    MONGODB_URI: str = "mongodb://localhost:27017"
    QDRANT_URL: str = "http://localhost:6333"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Instantiate a global settings object to be imported across the app
settings = Settings()
