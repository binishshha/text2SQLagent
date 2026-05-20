import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is required")


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def execute_query(sql: str):
    sql = sql.strip().rstrip(";")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

            if cur.description:
                return cur.fetchall()
            return []
