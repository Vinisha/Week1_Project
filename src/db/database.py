"""SQLite connection and schema setup."""
import sqlite3

from utils.paths import DB_PATH, ensure_dirs


def get_connection() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist. Safe to call on every startup."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meals (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                date      TEXT NOT NULL,            -- ISO YYYY-MM-DD
                meal_type TEXT NOT NULL,            -- Breakfast/Lunch/Dinner/Snack
                notes     TEXT DEFAULT ''
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meal_ingredients (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_id     INTEGER NOT NULL,
                ingredient  TEXT NOT NULL,
                category    TEXT NOT NULL,
                quantity_g  REAL NOT NULL,
                FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date)")
