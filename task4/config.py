from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/classicmodels",
        alias="DATABASE_URL",
    )
    max_result_rows: int = Field(default=100, alias="MAX_RESULT_ROWS")
    sql_statement_timeout_ms: int = Field(default=10_000, alias="SQL_STATEMENT_TIMEOUT_MS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
