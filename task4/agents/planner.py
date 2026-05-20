import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from prompts import PLANNER_SYSTEM_PROMPT


def _parse_json_object(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").removeprefix("json").strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Planner returned invalid JSON: {content}")

    return json.loads(cleaned[start : end + 1])


def create_plan(question: str) -> dict[str, Any]:
    llm = get_llm(temperature=0.0)
    response = llm.invoke(
        [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
    )
    try:
        plan = _parse_json_object(str(response.content))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Planner returned invalid JSON: {response.content}") from exc

    if "can_answer" not in plan:
        plan["can_answer"] = True
    return plan
