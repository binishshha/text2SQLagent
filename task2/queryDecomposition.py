"""
Task 2: Query Decomposition for Agentic Text-to-SQL pipeline.

This script:
1. Loads GEMINI_API_KEY from .env.
2. Reads questions from data/sql_questions.csv.
3. Calls Gemini 2.5 Flash with strict system instructions.
4. Writes decomposed outputs to task2_decomposed_answers.csv.
5. Retries transient failures and logs errors safely.
"""

from __future__ import annotations

import csv
import json
import os
import re
import time
from pathlib import Path
from typing import Callable, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

# =========================
# PROMPT CONFIG
# =========================

SYSTEM_INSTRUCTION = """You are an expert SQL query decomposition assistant.

Given a natural language analytics question, decompose it into exactly these 5 lines and nothing else:
Intent: [Goal]
Tables: [Tables involved]
Columns: [Columns needed]
Filters: [Conditions or 'None']
Joins: [ON conditions or 'None']

Rules:
- Output exactly five lines in the exact labels/order above.
- Use only tables/columns that exist in the schema.
- If unknown, infer most likely schema elements.
- No markdown, no bullets, no explanations, no extra text.
"""

BATCH_SYSTEM_INSTRUCTION = """You are an expert SQL query decomposition assistant.

Given a list of natural language analytics questions, return a JSON array only.
Each array item must have exactly these keys:
question_no, Intent, Tables, Columns, Filters, Joins

Rules:
- Return valid JSON only. No markdown, no code fences, no explanations.
- Include one item for every input question.
- Use only tables/columns that exist in the schema.
- If unknown, infer most likely schema elements.
- Use "None" for Filters or Joins when not needed.
"""

SCHEMA_CONTEXT = """Sample database schema:

customers(customerNumber PK, customerName, contactLastName, contactFirstName, phone, addressLine1, city, state, postalCode, country, salesRepEmployeeNumber FK, creditLimit)

orders(orderNumber PK, orderDate, requiredDate, shippedDate, status, comments, customerNumber FK)

orderdetails(orderNumber FK, productCode FK, quantityOrdered, priceEach, orderLineNumber)

products(productCode PK, productName, productLine, productScale, productVendor, quantityInStock, buyPrice, MSRP)

payments(customerNumber FK, checkNumber, paymentDate, amount)

employees(employeeNumber PK, lastName, firstName, extension, email, officeCode FK, reportsTo FK, jobTitle)

offices(officeCode PK, city, phone, addressLine1, state, country, postalCode, territory)
"""

EXPECTED_LABELS = ["Intent", "Tables", "Columns", "Filters", "Joins"]
OUTPUT_FIELDS = [
    "ID",
    "Question",
    "Intent",
    "Tables",
    "Columns",
    "Filters",
    "Joins",
    "Raw_JSON",
]

REQUESTS_PER_MINUTE = 5
REQUEST_INTERVAL_SECONDS = 15
RATE_LIMIT_COOLDOWN_SECONDS = 90


# =========================
# UTILITIES
# =========================


def validate_and_normalize_output(text: str) -> str:
    """Ensure strict 5-line structured output."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]

    extracted = {k: "None" for k in EXPECTED_LABELS}

    for line in lines:
        for label in EXPECTED_LABELS:
            match = re.match(rf"^{label}\s*:\s*(.*)$", line, re.I)
            if match:
                extracted[label] = match.group(1).strip() or "None"

    return "\n".join(f"{k}: {extracted[k]}" for k in EXPECTED_LABELS)


def format_decomposition(item: dict) -> str:
    """Convert a batch JSON item into the required 5-line output."""
    extracted = {
        label: str(item.get(label) or "None").strip() or "None"
        for label in EXPECTED_LABELS
    }
    return "\n".join(f"{k}: {extracted[k]}" for k in EXPECTED_LABELS)


def normalize_batch_item(item: dict) -> dict:
    """Normalize Gemini output to the requested CSV columns."""
    return {
        label: str(item.get(label) or "None").strip() or "None"
        for label in EXPECTED_LABELS
    }


def make_output_row(question_no: int, question: str, item: dict) -> dict:
    """Build one output row with separate decomposition columns."""
    normalized = normalize_batch_item(item)
    row_json = {
        "intent": normalized["Intent"],
        "tables": normalized["Tables"],
        "columns": normalized["Columns"],
        "filters": normalized["Filters"],
        "joins": normalized["Joins"],
    }
    return {
        "ID": question_no,
        "Question": question,
        "Intent": normalized["Intent"],
        "Tables": normalized["Tables"],
        "Columns": normalized["Columns"],
        "Filters": normalized["Filters"],
        "Joins": normalized["Joins"],
        "Raw_JSON": json.dumps(row_json, ensure_ascii=False, separators=(",", ":")),
    }


def extract_json_array(text: str) -> list[dict]:
    """Parse a JSON array, tolerating accidental markdown fences around it."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", cleaned)
        if not match:
            raise
        parsed = json.loads(match.group(0))

    if not isinstance(parsed, list):
        raise ValueError("Batch response was not a JSON array")

    return parsed


def serialize_response(resp: object) -> str:
    """Best-effort Gemini response serialization."""
    if hasattr(resp, "model_dump_json"):
        try:
            return resp.model_dump_json()
        except Exception:
            pass

    if hasattr(resp, "model_dump"):
        try:
            return json.dumps(resp.model_dump(), ensure_ascii=False)
        except Exception:
            pass

    return json.dumps({"raw": str(resp)}, ensure_ascii=False)


def is_rate_limit_error(error: Exception) -> bool:
    """Detect Gemini quota/rate-limit failures from SDK exception text."""
    message = str(error).lower()
    rate_limit_markers = (
        "429",
        "rate limit",
        "quota",
        "resource_exhausted",
        "requests per minute",
        "allowed 5 requests per minute",
    )
    return any(marker in message for marker in rate_limit_markers)


def is_daily_quota_error(error: Exception) -> bool:
    """Detect daily quota exhaustion, where retrying now will not help."""
    message = str(error).lower()
    daily_quota_markers = (
        "perday",
        "per day",
        "requests per day",
        "generaterequestsperday",
        "free_tier_requests",
    )
    return any(marker in message for marker in daily_quota_markers)


class RateLimiter:
    """Simple process-local limiter for Gemini requests."""

    def __init__(
        self,
        interval_seconds: float = REQUEST_INTERVAL_SECONDS,
        sleep_fn: Callable[[float], None] = time.sleep,
    ):
        self.interval_seconds = interval_seconds
        self.sleep_fn = sleep_fn
        self.last_request_at: float | None = None

    def wait(self) -> None:
        if self.last_request_at is None:
            return

        elapsed = time.monotonic() - self.last_request_at
        wait_seconds = self.interval_seconds - elapsed

        if wait_seconds > 0:
            print(
                f"[RATE LIMIT] Sleeping {wait_seconds:.1f}s to stay within 5 requests/minute"
            )
            self.sleep_fn(wait_seconds)

    def mark_request(self) -> None:
        self.last_request_at = time.monotonic()


# =========================
# GEMINI CALL
# =========================


def call_gemini_with_retry(
    client: genai.Client,
    model: str,
    question: str,
    rate_limiter: RateLimiter,
    max_retries: int = 5,
    initial_delay: float = 1.5,
) -> tuple[str, str]:

    prompt = f"{SCHEMA_CONTEXT}\nQuestion: {question}\n"

    for attempt in range(1, max_retries + 1):
        try:
            rate_limiter.wait()
            rate_limiter.mark_request()
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.0,
                ),
            )

            text = (response.text or "").strip()
            if not text:
                raise ValueError("Empty response")

            return validate_and_normalize_output(text), serialize_response(response)

        except Exception as e:
            if is_daily_quota_error(e):
                raise RuntimeError(
                    "Daily Gemini quota exhausted for this model/project. "
                    "Progress has been saved; rerun after the quota resets or use a key/project with higher quota."
                ) from e

            if attempt == max_retries:
                raise RuntimeError(f"Gemini failed after retries: {e}") from e

            if is_rate_limit_error(e):
                sleep_time = RATE_LIMIT_COOLDOWN_SECONDS
                print(
                    f"[WARN] Rate limit hit on attempt {attempt}: {e} | "
                    f"cooling down {sleep_time:.1f}s"
                )
            else:
                sleep_time = initial_delay * (2 ** (attempt - 1))
                print(f"[WARN] Retry {attempt}: {e} | sleeping {sleep_time:.1f}s")

            time.sleep(sleep_time)

    raise RuntimeError("Unexpected retry failure")


def call_gemini_batch_with_retry(
    client: genai.Client,
    model: str,
    numbered_questions: List[tuple[int, str]],
    rate_limiter: RateLimiter,
    max_retries: int = 5,
    initial_delay: float = 2.0,
) -> tuple[list[dict], str]:
    questions_json = json.dumps(
        [
            {"question_no": number, "question": question}
            for number, question in numbered_questions
        ],
        ensure_ascii=False,
        indent=2,
    )
    prompt = f"{SCHEMA_CONTEXT}\nQuestions:\n{questions_json}\n"

    for attempt in range(1, max_retries + 1):
        try:
            rate_limiter.wait()
            rate_limiter.mark_request()
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=BATCH_SYSTEM_INSTRUCTION,
                    temperature=0.0,
                    response_mime_type="application/json",
                ),
            )

            text = (response.text or "").strip()
            if not text:
                raise ValueError("Empty batch response")

            return extract_json_array(text), serialize_response(response)

        except Exception as e:
            if is_daily_quota_error(e):
                raise RuntimeError(
                    "Daily Gemini quota exhausted for this model/project. "
                    "The batch request could not run until quota resets or a higher-quota key/project is used."
                ) from e

            if attempt == max_retries:
                raise RuntimeError(f"Gemini batch failed after retries: {e}") from e

            if is_rate_limit_error(e):
                sleep_time = RATE_LIMIT_COOLDOWN_SECONDS
                print(
                    f"[WARN] Rate limit hit on batch attempt {attempt}: {e} | "
                    f"cooling down {sleep_time:.1f}s before retrying"
                )
            else:
                sleep_time = initial_delay * (2 ** (attempt - 1))
                print(f"[WARN] Batch retry {attempt}: {e} | sleeping {sleep_time:.1f}s")

            time.sleep(sleep_time)

    raise RuntimeError("Unexpected batch retry failure")


# =========================
# DATA LOADING
# =========================


def read_questions(csv_path: Path) -> List[str]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    questions = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            if row and row[0].strip():
                questions.append(row[0].strip())

    if not questions:
        raise ValueError("No questions found in CSV")

    return questions


# =========================
# OUTPUT
# =========================


def write_outputs(path: Path, rows: List[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_existing_results(path: Path) -> List[dict]:
    """Load previous output so interrupted runs can resume without re-calling Gemini."""
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != OUTPUT_FIELDS:
            print(
                "Existing output uses an old format; regenerating with the requested columns."
            )
            return []
        return list(reader)


# ➕ NEW FUNCTION (ADDED ONLY)
def write_json_outputs(path: Path, rows: List[dict]) -> None:
    """Write results to JSON file (added feature, no change to existing logic)."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


# =========================
# MAIN
# =========================


def main():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"

    load_dotenv(project_root / ".env")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing GEMINI_API_KEY in .env")

    client = genai.Client(api_key=api_key)
    model = "gemini-2.5-flash"

    input_csv = data_dir / "sql_questions.csv"
    output_csv = Path(__file__).resolve().parent / "task2_decomposed_answers.csv"

    # ➕ NEW JSON OUTPUT PATH (ADDED ONLY)
    output_json = Path(__file__).resolve().parent / "task2_decomposed_answers.json"

    questions = read_questions(input_csv)

    print(f"Loaded {len(questions)} questions from {input_csv}")

    results = read_existing_results(output_csv)
    completed_questions = {
        row.get("Question") for row in results if row.get("Question")
    }
    rate_limiter = RateLimiter()

    if results:
        print(f"Resuming with {len(results)} saved result(s) from {output_csv}")

    pending_questions = [
        (i, q) for i, q in enumerate(questions, 1) if q not in completed_questions
    ]

    if pending_questions:
        print(
            f"Processing {len(pending_questions)} unfinished question(s) in one batch request..."
        )

        try:
            batch_items, _raw = call_gemini_batch_with_retry(
                client,
                model,
                pending_questions,
                rate_limiter,
            )
            batch_by_number = {
                int(item.get("question_no")): item
                for item in batch_items
                if str(item.get("question_no", "")).isdigit()
            }

            for question_no, question in pending_questions:
                item = batch_by_number.get(question_no, {})
                results.append(make_output_row(question_no, question, item))

            results.sort(key=lambda row: int(row["ID"]))
            write_outputs(output_csv, results)
            write_json_outputs(output_json, results)

        except Exception as e:
            print(f"[ERROR] {e}")
            write_outputs(output_csv, results)
            write_json_outputs(output_json, results)
            print(f"Partial CSV saved -> {output_csv}")
            print(f"Partial JSON saved -> {output_json}")
    else:
        print("All questions already completed.")

    write_outputs(output_csv, results)

    # ➕ NEW JSON WRITE (ADDED ONLY)
    write_json_outputs(output_json, results)

    print(f"Done → {output_csv}")
    print(f"JSON → {output_json}")


if __name__ == "__main__":
    main()
