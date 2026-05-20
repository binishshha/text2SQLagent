from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from graph.workflow import run_text_to_sql


app = FastAPI(
    title="Agentic Text-to-SQL API",
    description="Plans, generates, validates, executes, and summarizes PostgreSQL queries.",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["Which customers have the highest total payments?"])


class QueryResponse(BaseModel):
    question: str
    answer: str
    sql: str | None = None
    rows: list[dict[str, Any]] = []
    plan: dict[str, Any] | None = None
    error: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    try:
        state = run_text_to_sql(request.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return QueryResponse(
        question=request.question,
        answer=state.get("answer", ""),
        sql=state.get("sql"),
        rows=state.get("rows", []),
        plan=state.get("plan"),
        error=state.get("error"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
