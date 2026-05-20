import re

BLOCKED_KEYWORDS = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
KEYWORD_PATTERN = re.compile(
    r"\b(?:DELETE|DROP|UPDATE|INSERT|ALTER|TRUNCATE)\b", re.IGNORECASE
)


def validate_sql(sql: str):
    if not sql or not isinstance(sql, str):
        raise ValueError("SQL must be a non-empty string")

    cleaned_sql = sql.strip().rstrip(";")
    if not cleaned_sql.lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed")

    if KEYWORD_PATTERN.search(cleaned_sql):
        raise ValueError("Blocked keyword detected in SQL statement")

    return cleaned_sql
