import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from prompts import SUMMARIZER_SYSTEM_PROMPT


def summarize_results(question: str, sql: str, rows: list[dict[str, Any]]) -> str:
    llm = get_llm(temperature=0.2)
    response = llm.invoke(
        [
            SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"User question: {question}\n\n"
                    f"SQL executed: {sql}\n\n"
                    f"Result rows as JSON:\n{json.dumps(rows, default=str, indent=2)}"
                )
            ),
        ]
    )
    return str(response.content).strip()
