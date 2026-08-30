from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FORTYGUARD_API_KEY: str = "478cf77a2c2588b4d1ddb683a69563dc"
    FORTYGUARD_BASE_URL: str = "https://api.fortyguard.com/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./heatguard.db"
    POLL_INTERVAL_SECONDS: int = 3
    MAX_POLL_ATTEMPTS: int = 60
    FORTYGUARD_TIMEOUT_SECONDS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
