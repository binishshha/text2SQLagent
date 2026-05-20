"""Central configuration loading and validation for the Text2SQL agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - config can still explain the issue.
    load_dotenv = None


ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"
DEFAULT_MODEL = "gemini-2.5-flash"


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from .env and optional CLI arguments."""

    gemini_api_key: str
    gemini_model: str
    database_url: str | None
    postgres_host: str
    postgres_port: str
    postgres_db: str
    postgres_user: str
    postgres_password: str


def load_environment() -> None:
    """Load environment variables from the project .env file."""
    if load_dotenv is None:
        return
    load_dotenv(ENV_PATH)


def get_env_value(*names: str, default: str | None = None) -> str | None:
    """Return the first non-empty environment variable from the given names."""
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def load_settings(model_override: str | None = None) -> Settings:
    """Create a Settings object from .env values."""
    load_environment()

    api_key = get_env_value("GEMINI_API_KEY", "gemini_api_key")
    if not api_key:
        raise EnvironmentError(
            "Gemini API key not found. Add GEMINI_API_KEY or gemini_api_key "
            "to .env using .env.template as a guide."
        )

    return Settings(
        gemini_api_key=api_key,
        gemini_model=model_override
        or get_env_value("GEMINI_MODEL", "gemini_model", default=DEFAULT_MODEL)
        or DEFAULT_MODEL,
        database_url=get_env_value("DATABASE_URL"),
        postgres_host=get_env_value("POSTGRES_HOST", default="localhost") or "localhost",
        postgres_port=get_env_value("POSTGRES_PORT", default="5432") or "5432",
        postgres_db=get_env_value("POSTGRES_DB", default="text2sql_agent") or "text2sql_agent",
        postgres_user=get_env_value("POSTGRES_USER", default="postgres") or "postgres",
        postgres_password=get_env_value("POSTGRES_PASSWORD", default="") or "",
    )


def build_postgres_dsn(settings: Settings) -> str:
    """Build a psycopg connection string from Settings."""
    if settings.database_url:
        return settings.database_url

    return (
        f"host={settings.postgres_host} "
        f"port={settings.postgres_port} "
        f"dbname={settings.postgres_db} "
        f"user={settings.postgres_user} "
        f"password={settings.postgres_password}"
    )


def mask_secret(value: str, visible: int = 4) -> str:
    """Mask a secret while keeping enough characters to identify it locally."""
    if len(value) <= visible:
        return "*" * len(value)
    return f"{value[:visible]}{'*' * max(len(value) - visible, 4)}"


def check_configuration() -> list[str]:
    """Return human-readable configuration check results."""
    results: list[str] = []

    if ENV_PATH.exists():
        results.append(f"OK .env found: {ENV_PATH}")
    else:
        results.append(f"MISSING .env file: copy .env.template to {ENV_PATH}")

    if load_dotenv is None:
        results.append("MISSING python-dotenv package: run pip install -r requirements.txt")

    try:
        settings = load_settings()
    except Exception as exc:
        results.append(f"ERROR {exc}")
        return results

    results.append(f"OK Gemini API key loaded: {mask_secret(settings.gemini_api_key)}")
    results.append(f"OK Gemini model: {settings.gemini_model}")

    if settings.database_url:
        results.append("OK PostgreSQL DATABASE_URL is set")
    else:
        results.append(f"OK PostgreSQL host: {settings.postgres_host}")
        results.append(f"OK PostgreSQL port: {settings.postgres_port}")
        results.append(f"OK PostgreSQL database: {settings.postgres_db}")
        results.append(f"OK PostgreSQL user: {settings.postgres_user}")
        if settings.postgres_password:
            results.append("OK PostgreSQL password is set")
        else:
            results.append("WARN PostgreSQL password is empty")

    if not settings.postgres_port.isdigit():
        results.append("ERROR POSTGRES_PORT must be a number")

    return results


def main() -> None:
    """CLI entrypoint for checking configuration."""
    for line in check_configuration():
        print(line)


if __name__ == "__main__":
    main()
