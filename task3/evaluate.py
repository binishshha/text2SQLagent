from executor import run_pipeline
import json
from pathlib import Path

DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "task2" / "task2_decomposed_answers.json"
)

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    DATASET = json.load(f)


def normalize(sql: str) -> str:
    return " ".join(sql.lower().strip().rstrip(";").split())


def main():
    total = len(DATASET)
    success = 0
    failed = 0

    for item in DATASET:

        # ✅ FIX: your dataset uses "Question", NOT "question"
        question = item.get("Question") or item.get("question")

        if not question:
            print("Skipping invalid row:", item)
            continue

        output = run_pipeline(question)

        sql = output.get("sql", "")
        status = output.get("status")

        if status == "success":
            success += 1
        else:
            failed += 1

        print("\nQuestion:", question)
        print("SQL:", sql)
        print("Status:", status)

    print("\n===== SUMMARY =====")
    print("Total:", total)
    print("Success:", success)
    print("Failed:", failed)


if __name__ == "__main__":
    main()
