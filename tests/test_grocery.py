"""Tests for the weekly grocery list aggregation."""
from datetime import date

import pandas as pd

from core.grocery import grocery_list_for_week, to_text


def _week_logs():
    # Same ingredient logged twice in the week should be summed.
    return pd.DataFrame(
        [
            {"meal_id": 1, "date": date(2026, 1, 5), "meal_type": "Lunch",
             "ingredient": "Rice", "category": "grain", "quantity_g": 200.0},
            {"meal_id": 2, "date": date(2026, 1, 7), "meal_type": "Dinner",
             "ingredient": "Rice", "category": "grain", "quantity_g": 150.0},
            {"meal_id": 2, "date": date(2026, 1, 7), "meal_type": "Dinner",
             "ingredient": "Spinach", "category": "vegetable", "quantity_g": 100.0},
        ]
    )


def test_same_ingredient_is_summed():
    g = grocery_list_for_week(_week_logs())
    rice = g[g["ingredient"] == "Rice"].iloc[0]
    assert rice["total_g"] == 350.0
    assert rice["total_kg"] == 0.35


def test_lists_all_distinct_ingredients():
    g = grocery_list_for_week(_week_logs())
    assert set(g["ingredient"]) == {"Rice", "Spinach"}


def test_text_render_has_checkboxes():
    g = grocery_list_for_week(_week_logs())
    text = to_text(g, date(2026, 1, 5), date(2026, 1, 11))
    assert "[ ]" in text
    assert "Rice" in text


def test_empty_week_is_safe():
    empty = pd.DataFrame(columns=["meal_id", "date", "meal_type",
                                  "ingredient", "category", "quantity_g"])
    assert grocery_list_for_week(empty).empty
