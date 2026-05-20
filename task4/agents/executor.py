from typing import Any

from tools.db_tools import execute_read_only_query


def execute_sql(sql: str) -> list[dict[str, Any]]:
    return execute_read_only_query(sql)
