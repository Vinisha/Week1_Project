"""CRUD operations over the meals / meal_ingredients tables."""
from datetime import date

import pandas as pd

from db.database import get_connection


def add_meal(meal_date: date, meal_type: str, ingredients: list, notes: str = "") -> int:
    """Persist one meal and its ingredients.

    ``ingredients`` is a list of dicts: {ingredient, category, quantity_g}.
    Returns the new meal id.
    """
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO meals (date, meal_type, notes) VALUES (?, ?, ?)",
            (meal_date.isoformat(), meal_type, notes),
        )
        meal_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO meal_ingredients (meal_id, ingredient, category, quantity_g) "
            "VALUES (?, ?, ?, ?)",
            [
                (meal_id, i["ingredient"], i["category"], float(i["quantity_g"]))
                for i in ingredients
            ],
        )
        return meal_id


def delete_meal(meal_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM meals WHERE id = ?", (meal_id,))


def get_logs(start: date, end: date) -> pd.DataFrame:
    """Return one row per logged ingredient between start and end (inclusive).

    Columns: meal_id, date, meal_type, ingredient, category, quantity_g.
    ``date`` is returned as a python date for easy grouping.
    """
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT m.id AS meal_id, m.date, m.meal_type, m.notes,
                   mi.ingredient, mi.category, mi.quantity_g
            FROM meals m
            JOIN meal_ingredients mi ON mi.meal_id = m.id
            WHERE m.date BETWEEN ? AND ?
            ORDER BY m.date, m.id
            """,
            conn,
            params=(start.isoformat(), end.isoformat()),
        )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def get_meals_summary(start: date, end: date) -> pd.DataFrame:
    """One row per meal (no ingredient fan-out) for listing/management UIs."""
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT m.id AS meal_id, m.date, m.meal_type, m.notes,
                   COUNT(mi.id) AS n_ingredients
            FROM meals m
            LEFT JOIN meal_ingredients mi ON mi.meal_id = m.id
            WHERE m.date BETWEEN ? AND ?
            GROUP BY m.id
            ORDER BY m.date DESC, m.id DESC
            """,
            conn,
            params=(start.isoformat(), end.isoformat()),
        )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df
