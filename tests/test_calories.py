"""Tests for calorie/nutrient enrichment and daily aggregation."""
from datetime import date

import pandas as pd

from core.calories import enrich_logs, daily_totals, period_totals


def _logs():
    # 200 g Rice (130 kcal/100g) -> 260 kcal; 100 g Egg (155/100g) -> 155 kcal
    return pd.DataFrame(
        [
            {"meal_id": 1, "date": date(2026, 1, 5), "meal_type": "Lunch",
             "ingredient": "Rice", "category": "grain", "quantity_g": 200.0},
            {"meal_id": 1, "date": date(2026, 1, 5), "meal_type": "Lunch",
             "ingredient": "Egg", "category": "non-veg", "quantity_g": 100.0},
        ]
    )


def test_enrich_scales_by_quantity():
    enriched = enrich_logs(_logs())
    rice = enriched[enriched["ingredient"] == "Rice"].iloc[0]
    assert round(rice["calories"], 1) == 260.0  # 130 * 200/100


def test_unknown_ingredient_contributes_zero():
    logs = _logs()
    logs.loc[len(logs)] = {"meal_id": 1, "date": date(2026, 1, 5),
                           "meal_type": "Lunch", "ingredient": "Moon Cheese",
                           "category": "other", "quantity_g": 500.0}
    enriched = enrich_logs(logs)
    unknown = enriched[enriched["ingredient"] == "Moon Cheese"].iloc[0]
    assert unknown["calories"] == 0.0


def test_daily_totals_sums_per_day():
    daily = daily_totals(enrich_logs(_logs()))
    assert len(daily) == 1
    assert round(daily.iloc[0]["calories"], 1) == 415.0  # 260 + 155


def test_period_totals_groups_by_week():
    period = period_totals(enrich_logs(_logs()), by="week")
    assert period.iloc[0]["days"] == 1
    assert round(period.iloc[0]["calories"], 1) == 415.0


def test_empty_logs_safe():
    empty = pd.DataFrame(columns=["meal_id", "date", "meal_type",
                                  "ingredient", "category", "quantity_g"])
    assert daily_totals(enrich_logs(empty)).empty
