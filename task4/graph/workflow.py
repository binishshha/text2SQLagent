from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from agents.executor import execute_sql
from agents.planner import create_plan
from agents.sql_generator import generate_sql
from agents.summarizer import summarize_results
from agents.validator import validate_sql


class TextToSQLState(TypedDict, total=False):
    question: str
    plan: dict[str, Any]
    sql: str
    rows: list[dict[str, Any]]
    answer: str
    error: str
    validation_error: str


def planner_node(state: TextToSQLState) -> TextToSQLState:
    plan = create_plan(state["question"])
    return {"plan": plan}


def route_after_planner(state: TextToSQLState) -> Literal["generate_sql", "end_with_error"]:
    if state.get("plan", {}).get("can_answer", True):
        return "generate_sql"
    return "end_with_error"


def end_with_error_node(state: TextToSQLState) -> TextToSQLState:
    notes = state.get("plan", {}).get("notes") or "This request cannot be answered safely."
    return {"error": notes, "answer": notes}


def sql_generator_node(state: TextToSQLState) -> TextToSQLState:
    sql = generate_sql(state["question"], state["plan"])
    return {"sql": sql}


def validator_node(state: TextToSQLState) -> TextToSQLState:
    result = validate_sql(state["sql"])
    if not result.is_valid:
        return {"validation_error": result.reason, "error": result.reason}
    return {"sql": result.sql, "validation_error": ""}


def route_after_validator(state: TextToSQLState) -> Literal["execute_sql", "end_after_validation_error"]:
    if state.get("validation_error"):
        return "end_after_validation_error"
    return "execute_sql"


def end_after_validation_error_node(state: TextToSQLState) -> TextToSQLState:
    message = f"I could not safely validate the generated SQL: {state.get('validation_error')}"
    return {"answer": message}


def executor_node(state: TextToSQLState) -> TextToSQLState:
    rows = execute_sql(state["sql"])
    return {"rows": rows}


def summarizer_node(state: TextToSQLState) -> TextToSQLState:
    answer = summarize_results(state["question"], state["sql"], state.get("rows", []))
    return {"answer": answer}


def build_workflow():
    graph = StateGraph(TextToSQLState)

    graph.add_node("planner", planner_node)
    graph.add_node("generate_sql", sql_generator_node)
    graph.add_node("validate_sql", validator_node)
    graph.add_node("execute_sql", executor_node)
    graph.add_node("summarize", summarizer_node)
    graph.add_node("end_with_error", end_with_error_node)
    graph.add_node("end_after_validation_error", end_after_validation_error_node)

    graph.set_entry_point("planner")
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {"generate_sql": "generate_sql", "end_with_error": "end_with_error"},
    )
    graph.add_edge("generate_sql", "validate_sql")
    graph.add_conditional_edges(
        "validate_sql",
        route_after_validator,
        {
            "execute_sql": "execute_sql",
            "end_after_validation_error": "end_after_validation_error",
        },
    )
    graph.add_edge("execute_sql", "summarize")
    graph.add_edge("summarize", END)
    graph.add_edge("end_with_error", END)
    graph.add_edge("end_after_validation_error", END)

    return graph.compile()


workflow = build_workflow()


def run_text_to_sql(question: str) -> TextToSQLState:
    return workflow.invoke({"question": question})
