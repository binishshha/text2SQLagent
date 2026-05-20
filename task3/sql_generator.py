import json
import os
from dotenv import load_dotenv
from google import genai

from prompts.templates import (
    DECOMPOSITION_PROMPT,
    GENERATION_PROMPT,
    FIX_PROMPT,
    SCHEMA_CONTEXT,
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")


def _call_llm(prompt: str):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        print("RAW RESPONSE:", response)

        return response.text

    except Exception as e:
        print("LLM ERROR:", e)
        raise


def _extract_json(raw_text: str) -> dict:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        first = raw_text.find("{")
        last = raw_text.rfind("}")
        if first != -1 and last != -1:
            return json.loads(raw_text[first : last + 1])
        raise


def decompose_question(question: str) -> dict:
    prompt = DECOMPOSITION_PROMPT.format(question=question)
    raw = _call_llm(prompt)

    try:
        return _extract_json(raw)
    except Exception:
        return {
            "Intent": "SELECT",
            "Tables": [],
            "Columns": [],
            "Filters": [],
            "Joins": [],
        }


def generate_sql(decomposition: dict) -> str:
    prompt = GENERATION_PROMPT.format(
        schema=SCHEMA_CONTEXT,
        decomposition=json.dumps(decomposition, indent=2),
    )

    raw_response = _call_llm(prompt)

    print("DEBUG LLM RESPONSE:\n", raw_response)

    sql = raw_response.strip()
    sql = sql.replace("```sql", "").replace("```", "")
    return sql.rstrip(";").strip()


def fix_sql(original_sql: str, error_message: str) -> str:
    prompt = FIX_PROMPT.format(sql=original_sql, error=error_message)
    raw = _call_llm(prompt)

    sql = raw.strip().replace("```sql", "").replace("```", "")
    return sql.rstrip(";").strip()
