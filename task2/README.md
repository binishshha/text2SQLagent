# Task 2: Query Decomposition

This script reads natural-language questions from `data/sql_questions.csv`,
uses Gemini 2.5 Flash to decompose each question, and writes structured outputs
for the Text-to-SQL pipeline.

## Setup

1. Install the Task 2 dependencies:

```bash
pip install -r requirements.txt
```

2. Put your Gemini key in `.env`:

```env
gemini_api_key=your_real_key_here
GEMINI_MODEL=gemini-2.5-flash
```

3. Check your configuration:

```bash
python config.py
```

## Run Batch Decomposition

From the project root:

```bash
python "task2/queryDecomposition.py"
```

## Decompose One Question

From the project root:

```bash
python "task2/queryDecomposition.py" --question "List all customers from USA"
```

Optional quick test:

```bash
python "task2/queryDecomposition.py" --limit 3
```

## Output

The script creates:

- `task2/outputs/task2_decomposed_answers.csv`
- `task2/outputs/task2_decomposed_answers.json`

Each row contains:

- Intent
- Tables involved
- Columns needed
- Filters/conditions
- Joins

## What This Task Achieves

Task 2 completes the query-understanding/decomposition stage of the agentic
Text-to-SQL pipeline using Gemini for the actual natural-language decomposition.
