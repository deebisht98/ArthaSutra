from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import sys

class Settings(BaseSettings):
    PROJECT_NAME: str = "Artha Sutra API"
    ENVIRONMENT: str = "development"

    # API Keys
    TAVILY_API_KEY: str
    OPENAI_API_KEY: str
    KITE_API_KEY: str
    KITE_API_SECRET: str

    # Database URLs
    MONGODB_URI: str
    QDRANT_URL: str

    # Operational Controls
    DRY_RUN: bool = Field(default=True)
    KILL_SWITCH_PCT: float = Field(default=10.0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator(
        "TAVILY_API_KEY",
        "OPENAI_API_KEY",
        "KITE_API_KEY",
        "KITE_API_SECRET",
        "MONGODB_URI",
        "QDRANT_URL"
    )
    @classmethod
    def check_not_empty(cls, v: str, info):
        if not v or v.strip() == "":
            raise ValueError(f"CRITICAL: {info.field_name} is missing or empty. System cannot start without this variable.")
        return v

# Instantiate settings to trigger validation on startup
try:
    settings = Settings()
except Exception as e:
    print(f"\nFATAL CONFIGURATION ERROR:\n{e}\n", file=sys.stderr)
    # Raising to prevent the app from starting with invalid configuration
    raise RuntimeError(f"Application failed to start due to configuration errors: {e}")
