import json
import os
from datetime import datetime
from database import execute_query
from sql_generator import decompose_question, generate_sql, fix_sql
from validator import validate_sql

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "query_logs.json")


def _ensure_log_file():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _append_log(entry: dict):
    _ensure_log_file()

    with open(LOG_FILE, "r+", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


def run_pipeline(question: str) -> dict:
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "sql": None,
        "status": "failed",
        "retry_needed": False,
        "error": None,
    }

    try:
        decomposition = decompose_question(question)
        sql = generate_sql(decomposition)
        sql = validate_sql(sql)
        entry["sql"] = sql

        try:
            result = execute_query(sql)

            entry["status"] = "success"
            entry["result_count"] = len(result)
            _append_log(entry)

            return {
                "question": question,
                "sql": sql,
                "result": result,
                "status": "success",
                "retry_needed": False,
            }

        except Exception as e:
            entry["error"] = str(e)
            entry["retry_needed"] = True

            fixed_sql = fix_sql(sql, str(e))
            fixed_sql = validate_sql(fixed_sql)
            entry["sql"] = fixed_sql

            try:
                result = execute_query(fixed_sql)

                entry["status"] = "success"
                entry["result_count"] = len(result)
                _append_log(entry)

                return {
                    "question": question,
                    "sql": fixed_sql,
                    "result": result,
                    "status": "success",
                    "retry_needed": True,
                }

            except Exception as e2:
                entry["status"] = "failed"
                entry["error"] = str(e2)
                _append_log(entry)

                return {
                    "question": question,
                    "sql": fixed_sql,
                    "result": [],
                    "status": "failed",
                    "retry_needed": True,
                    "error": str(e2),
                }

    except Exception as e:
        entry["error"] = str(e)
        _append_log(entry)

        return {
            "question": question,
            "sql": None,
            "result": [],
            "status": "failed",
            "retry_needed": False,
            "error": str(e),
        }
