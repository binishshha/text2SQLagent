# Text2SQL Agent - Week 3 AI Fellowship Project

A comprehensive project demonstrating the progression from basic SQL query execution to an intelligent SQL generation agent powered by language models and multi-agent orchestration.

## 📁 Project Structure

### Root Level Files

- **`config.py`** - Central configuration management for the entire project
- **`requirements.txt`** - Python dependencies for the base project
- **`data/`** - Data directory containing input datasets

---

## 📚 Main Directories

### 1. **`data/`** - Input Data

Contains raw data used for training and querying:

- **`sql_questions.csv`** - Dataset of SQL questions and their expected outputs

### 2. **`sql/`** - Database Setup Scripts

Database initialization and seeding:

- **`init.sql`** - Database schema initialization script
- **`seed.sql`** - Sample data for populating the database

### 3. **`task1/`** - Basic Query Execution

The foundation: executing pre-written SQL queries and validating results.

**Contents:**

- **`queries.sql`** - Collection of 50 pre-written SQL queries
- **`ground_truth_sql.csv`** - Expected outputs for all 50 queries
- **`Query Outputs/`** - Directory containing actual query results
  - `q01_result.csv` through `q50_result.csv` - Individual query output files

**Purpose:** Establishes baseline SQL execution and output validation

---

### 4. **`task2/`** - Query Decomposition

Breaking down complex SQL questions into smaller, manageable components.

**Contents:**

- **`queryDecomposition.py`** - Main decomposition logic that breaks queries into steps
- **`task2_decomposed_answers.csv`** - Decomposed query results in CSV format
- **`task2_decomposed_answers.json`** - Decomposed query results in JSON format
- **`README.md`** - Task-specific documentation

**Purpose:** Demonstrates query understanding and decomposition for complex SQL generation

---

### 5. **`task3/`** - SQL Generation with LLM

Generates SQL queries using a language model without explicit decomposition.

**Contents:**

- **`sql_generator.py`** - Core LLM-based SQL generation logic
- **`database.py`** - Database connection and management utilities
- **`executor.py`** - Executes generated SQL queries
- **`validator.py`** - Validates generated SQL correctness
- **`evaluate.py`** - Evaluation framework for query results
- **`test.py`** - Testing suite for SQL generation
- **`streamlit_app.py`** - Interactive web UI for SQL generation
- **`docker-compose.yml`** - Docker Compose configuration
- **`Dockerfile`** - Docker image specification
- **`requirements.txt`** - Task-specific Python dependencies
- **`prompts/`** - LLM prompt templates
  - `__init__.py` - Package initialization
  - `templates.py` - Prompt template definitions
- **`logs/`** - Execution logs
  - `query_logs.json` - Logged query execution data

**Purpose:** Single-stage SQL generation using language models

---

### 6. **`task4/`** - Multi-Agent SQL Generation System

Advanced system with orchestrated agents for planning, generation, validation, and summarization.

**Contents:**

#### Core Files

- **`main.py`** - Entry point for the multi-agent system
- **`streamlit_app.py`** - Interactive web interface
- **`docker-compose.yml`** - Docker Compose configuration
- **`Dockerfile`** - Container specification
- **`requirements.txt`** - Task-specific dependencies
- **`config.py`** - Task 4 configuration
- **`db.py`** - Database operations

#### Agents (`agents/`)

Specialized agents handling different aspects of SQL generation:

- **`planner.py`** - Decomposes questions and creates execution plans
- **`sql_generator.py`** - Generates SQL based on plans
- **`validator.py`** - Validates SQL syntax and semantics
- **`executor.py`** - Executes queries against the database
- **`summarizer.py`** - Summarizes query results
- **`llm.py`** - Language model interface and management

#### Workflow Graph (`graph/`)

Agent orchestration and workflow management:

- **`workflow.py`** - Defines the multi-agent workflow graph
- **`__init__.py`** - Package initialization

#### Supporting Components

- **`prompts/`** - LLM prompt templates
  - `__init__.py` - Package initialization
- **`sql/`** - Database setup
  - `seed.sql` - Sample data
- **`tools/`** - Utility tools
  - `db_tools.py` - Database utility functions

**Purpose:** Production-ready agent orchestration system for intelligent SQL generation

---

## 🚀 Quick Navigation Guide

### Understanding the Project Progression

```
Task 1: Execute pre-written queries
    ↓
Task 2: Decompose complex queries
    ↓
Task 3: Generate SQL with LLM (single stage)
    ↓
Task 4: Multi-agent orchestration system
```

### Getting Started

1. **Setup Database:**

   ```bash
   # Review database schema
   cat sql/init.sql
   cat sql/seed.sql
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   # Individual tasks may have their own requirements.txt
   ```

3. **Run Task 4 (Latest System):**

   ```bash
   cd task4
   python main.py
   # or
   streamlit run streamlit_app.py
   ```

4. **Using Docker:**
   ```bash
   cd task4
   docker-compose up --build
   ```

---

## 🔧 Configuration

- **Global Config:** `config.py` - Shared configuration across all tasks
- **Task-Specific Config:** `task4/config.py` - Task 4 specific settings

---

## 📊 Data Flow

```
SQL Questions (data/sql_questions.csv)
    ↓
Task 1: Execute & Validate Against Ground Truth
    ↓
Task 2: Decompose Complex Queries
    ↓
Task 3: LLM-Based SQL Generation
    ↓
Task 4: Multi-Agent System
    ├─ Planner Agent
    ├─ SQL Generator Agent
    ├─ Validator Agent
    ├─ Executor Agent
    └─ Summarizer Agent
```

---

## 📝 Key Files Reference

| Component           | File                          | Purpose                          |
| ------------------- | ----------------------------- | -------------------------------- |
| SQL Queries (Base)  | `task1/queries.sql`           | Pre-written SQL queries          |
| Ground Truth        | `task1/ground_truth_sql.csv`  | Expected query results           |
| Decomposition Logic | `task2/queryDecomposition.py` | Query breakdown algorithm        |
| LLM Generation      | `task3/sql_generator.py`      | Single-stage SQL generation      |
| Multi-Agent System  | `task4/main.py`               | Advanced orchestration           |
| Agent Definitions   | `task4/agents/*.py`           | Individual agent implementations |
| Workflow Logic      | `task4/graph/workflow.py`     | Agent coordination graph         |
| Web UI              | `task4/streamlit_app.py`      | Interactive interface            |

---

## 🔗 Dependencies

See the following files for required packages:

- `requirements.txt` - Base dependencies
- `task3/requirements.txt` - Task 3 specific
- `task4/requirements.txt` - Task 4 specific

---

## 📌 Notes

- Each task builds upon the previous one with increasing complexity
- Task 4 represents the final production-ready system
- Docker configurations are provided for containerized deployment
- Query results are logged in `task3/logs/query_logs.json` and task4 logs
- The Streamlit interface provides an accessible way to interact with the system

---

## 🎯 Next Steps

- Review `task4/agents/` to understand the agent architecture
- Check `task4/graph/workflow.py` for the execution flow
- Run `streamlit_app.py` in task4 to interact with the system
- Examine query logs to understand system behavior
