from dataclasses import dataclass

import sqlglot
from sqlglot import exp

from config import get_settings


FORBIDDEN_KEYWORDS = {
    "ALTER",
    "ANALYZE",
    "CALL",
    "COMMENT",
    "COMMIT",
    "COPY",
    "CREATE",
    "DELETE",
    "DO",
    "DROP",
    "EXECUTE",
    "GRANT",
    "INSERT",
    "MERGE",
    "REINDEX",
    "REVOKE",
    "ROLLBACK",
    "TRUNCATE",
    "UPDATE",
    "VACUUM",
}

ALLOWED_TABLES = {
    "productlines",
    "products",
    "offices",
    "employees",
    "customers",
    "payments",
    "orders",
    "orderdetails",
}


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    sql: str
    reason: str = ""


def validate_sql(sql: str) -> ValidationResult:
    candidate = sql.strip()
    if not candidate:
        return ValidationResult(False, candidate, "SQL is empty.")
    if ";" in candidate:
        return ValidationResult(False, candidate, "Semicolons and multiple statements are not allowed.")
    if "--" in candidate or "/*" in candidate or "*/" in candidate:
        return ValidationResult(False, candidate, "SQL comments are not allowed.")

    upper_tokens = {token.upper() for token in candidate.replace("\n", " ").split()}
    forbidden = sorted(upper_tokens.intersection(FORBIDDEN_KEYWORDS))
    if forbidden:
        return ValidationResult(False, candidate, f"Forbidden SQL keyword(s): {', '.join(forbidden)}.")

    try:
        parsed = sqlglot.parse_one(candidate, read="postgres")
    except sqlglot.errors.SqlglotError as exc:
        return ValidationResult(False, candidate, f"SQL parse error: {exc}.")

    if not isinstance(parsed, exp.Select):
        return ValidationResult(False, candidate, "Only SELECT statements are allowed.")

    disallowed = next(
        parsed.find_all(exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter, exp.Command),
        None,
    )
    if disallowed is not None:
        return ValidationResult(False, candidate, f"Disallowed SQL expression: {disallowed.key}.")

    for table in parsed.find_all(exp.Table):
        table_name = table.name
        if table_name not in ALLOWED_TABLES:
            return ValidationResult(False, candidate, f"Table is not allowlisted: {table_name}.")

    for column in parsed.find_all(exp.Column):
        if column.name == "image":
            return ValidationResult(False, candidate, 'Selecting "image" bytea data is not allowed.')

    if parsed.args.get("limit") is None:
        limit = get_settings().max_result_rows
        candidate = f"{candidate}\nLIMIT {limit}"

    return ValidationResult(True, candidate)
