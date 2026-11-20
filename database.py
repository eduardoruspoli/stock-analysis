import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "stock_analysis.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist (
                ticker TEXT PRIMARY KEY,
                added_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                ticker TEXT PRIMARY KEY,
                price REAL NOT NULL,
                change REAL NOT NULL,
                change_pct REAL NOT NULL,
                score INTEGER NOT NULL,
                recommendation TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def get_watchlist():
    with get_connection() as conn:
        rows = conn.execute("SELECT ticker FROM watchlist ORDER BY rowid").fetchall()
    return [row["ticker"] for row in rows]


def add_to_watchlist(ticker):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (ticker, added_at) VALUES (?, ?)",
            (ticker, datetime.now().isoformat(timespec="seconds")),
        )


def remove_from_watchlist(ticker):
    with get_connection() as conn:
        conn.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
        conn.execute("DELETE FROM snapshots WHERE ticker = ?", (ticker,))


def save_snapshot(ticker, price, change, change_pct, score, recommendation, updated_at):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO snapshots
                (ticker, price, change, change_pct, score, recommendation, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (ticker, price, change, change_pct, score, recommendation, updated_at),
        )


def get_snapshots():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM snapshots").fetchall()
    return {row["ticker"]: dict(row) for row in rows}
