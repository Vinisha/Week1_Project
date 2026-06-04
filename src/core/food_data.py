"""Load and update the editable food database (per-100g nutrient values)."""
import pandas as pd

from utils.paths import FOOD_DB_PATH
from core.settings import NUTRIENTS


def load_food_db() -> pd.DataFrame:
    """Return the food database as a DataFrame, one row per ingredient."""
    df = pd.read_csv(FOOD_DB_PATH)
    df["name"] = df["name"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    return df


def food_names() -> list:
    return sorted(load_food_db()["name"].tolist())


def lookup(name: str):
    """Return a single food's row as a dict, or None if not found (case-insensitive)."""
    df = load_food_db()
    match = df[df["name"].str.lower() == str(name).strip().lower()]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def add_food(name: str, category: str, values: dict) -> None:
    """Add a new ingredient to the food database (or overwrite if the name exists)."""
    df = load_food_db()
    name = name.strip()
    row = {"name": name, "category": category}
    for n in NUTRIENTS:
        row[n] = float(values.get(n, 0) or 0)
    # Drop an existing entry with the same name (case-insensitive), then append.
    df = df[df["name"].str.lower() != name.lower()]
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df = df.sort_values("name").reset_index(drop=True)
    df.to_csv(FOOD_DB_PATH, index=False)
