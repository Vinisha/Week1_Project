"""Populate the database with ~1 year of realistic sample meals.

Usage (from project root, with the venv active):
    python src/utils/seed_meals.py            # 365 days, clears existing data first
    python src/utils/seed_meals.py --days 120 # shorter span
    python src/utils/seed_meals.py --keep      # append instead of clearing

The data is intentionally varied — some days are skipped, snacks are
occasional, and a few nutrients (vitamin D, calcium) tend to run low so the
Deficiencies page has something to flag.
"""
import argparse
import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src
import bootstrap  # noqa: F401,E402  (path + db init)

from core.food_data import lookup  # noqa: E402
from db.database import get_connection  # noqa: E402
from db.repository import add_meal  # noqa: E402

# Meal templates: each entry is a list of (ingredient, (min_g, max_g)).
BREAKFASTS = [
    [("Oats", (40, 70)), ("Milk", (150, 250)), ("Banana", (80, 120))],
    [("Bread", (60, 100)), ("Egg", (50, 120)), ("Orange", (100, 150))],
    [("Oats", (40, 60)), ("Yogurt", (100, 180)), ("Apple", (100, 150)),
     ("Almonds", (15, 30))],
]
LUNCHES = [
    [("Rice", (150, 250)), ("Toor Dal", (100, 180)), ("Spinach", (80, 150)),
     ("Olive Oil", (5, 12))],
    [("Rice", (150, 250)), ("Chicken Breast", (120, 200)), ("Broccoli", (80, 150)),
     ("Olive Oil", (5, 12))],
    [("Wheat Flour", (80, 140)), ("Moong Dal", (100, 180)),
     ("Cauliflower", (80, 150)), ("Ghee", (5, 10))],
    [("Rice", (150, 250)), ("Kidney Beans", (120, 200)), ("Onion", (40, 80)),
     ("Tomato", (50, 100))],
]
DINNERS = [
    [("Rice", (120, 200)), ("Tilapia", (120, 200)), ("Bell Pepper", (60, 120))],
    [("Quinoa", (120, 200)), ("Chickpeas", (120, 200)), ("Carrot", (60, 120)),
     ("Olive Oil", (5, 12))],
    [("Wheat Flour", (80, 140)), ("Paneer", (80, 150)), ("Spinach", (80, 150)),
     ("Ghee", (5, 10))],
    [("Rice", (120, 200)), ("Shrimp", (100, 180)), ("Cabbage", (60, 120))],
    [("Rice", (120, 200)), ("Mutton", (120, 200)), ("Onion", (40, 80))],
]
SNACKS = [
    [("Apple", (100, 160))],
    [("Almonds", (20, 40))],
    [("Yogurt", (100, 150)), ("Banana", (80, 120))],
    [("Orange", (100, 160))],
]


def _to_ingredients(template):
    """Resolve a template into repository ingredient dicts with random quantities."""
    out = []
    for name, (lo, hi) in template:
        food = lookup(name)
        if not food:
            continue
        out.append({
            "ingredient": food["name"],
            "category": food["category"],
            "quantity_g": float(random.randint(lo, hi)),
        })
    return out


def clear_meals():
    with get_connection() as conn:
        conn.execute("DELETE FROM meal_ingredients")
        conn.execute("DELETE FROM meals")


def seed(days: int):
    today = date.today()
    start = today - timedelta(days=days - 1)
    n_meals = 0
    d = start
    while d <= today:
        # Skip ~8% of days entirely (travel, eating out, forgot to log).
        if random.random() < 0.08:
            d += timedelta(days=1)
            continue
        add_meal(d, "Breakfast", _to_ingredients(random.choice(BREAKFASTS)))
        add_meal(d, "Lunch", _to_ingredients(random.choice(LUNCHES)))
        add_meal(d, "Dinner", _to_ingredients(random.choice(DINNERS)))
        n_meals += 3
        # Snack on ~55% of days.
        if random.random() < 0.55:
            add_meal(d, "Snack", _to_ingredients(random.choice(SNACKS)))
            n_meals += 1
        d += timedelta(days=1)
    return n_meals, start, today


def main():
    parser = argparse.ArgumentParser(description="Seed sample nutrition data.")
    parser.add_argument("--days", type=int, default=365,
                        help="Number of days of history to generate (default 365).")
    parser.add_argument("--keep", action="store_true",
                        help="Append to existing data instead of clearing it.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducible data (default 42).")
    args = parser.parse_args()

    random.seed(args.seed)
    if not args.keep:
        clear_meals()
        print("Cleared existing meal data.")

    n_meals, start, end = seed(args.days)
    print(f"Seeded {n_meals} meals from {start} to {end} ({args.days} days).")
    print("Open the app and explore the Dashboard, Deficiencies and Grocery List.")


if __name__ == "__main__":
    main()
