import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from prompts import SQL_GENERATOR_SYSTEM_PROMPT


def _clean_sql(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("sql"):
            cleaned = cleaned[3:].strip()
    return cleaned.strip().rstrip(";").strip()


def generate_sql(question: str, plan: dict[str, Any]) -> str:
    llm = get_llm(temperature=0.0)
    response = llm.invoke(
        [
            SystemMessage(content=SQL_GENERATOR_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    "User question:\n"
                    f"{question}\n\n"
                    "Query plan JSON:\n"
                    f"{json.dumps(plan, indent=2)}"
                )
            ),
        ]
    )
    return _clean_sql(str(response.content))
