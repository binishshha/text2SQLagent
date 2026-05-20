from functools import lru_cache

from langchain_openai import ChatOpenAI

from config import get_settings


@lru_cache
def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for LLM-backed agents.")
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=temperature,
        api_key=settings.openai_api_key,
        timeout=30,
        max_retries=2,
    )
