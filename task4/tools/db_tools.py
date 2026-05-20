from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from config import get_settings
from db import SessionLocal


def execute_read_only_query(sql: str) -> list[dict[str, Any]]:
    settings = get_settings()
    with SessionLocal() as session:
        return execute_with_session(session, sql, settings.sql_statement_timeout_ms)


def execute_with_session(session: Session, sql: str, statement_timeout_ms: int) -> list[dict[str, Any]]:
    try:
        session.execute(text("SET TRANSACTION READ ONLY"))
        session.execute(text(f"SET LOCAL statement_timeout = {int(statement_timeout_ms)}"))
        result = session.execute(text(sql))
        rows = [dict(row._mapping) for row in result]
        return rows
    finally:
        session.rollback()
