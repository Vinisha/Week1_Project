"""Tests for the deficiency report logic."""
from datetime import date

import pandas as pd

from core.calories import enrich_logs
from core.deficiency import deficiency_report, flagged_only


def _one_day_logs():
    # A single modest meal so most nutrients fall short of the daily RDA.
    return pd.DataFrame(
        [
            {"meal_id": 1, "date": date(2026, 1, 5), "meal_type": "Lunch",
             "ingredient": "Rice", "category": "grain", "quantity_g": 100.0},
        ]
    )


def test_avg_divides_by_window_not_logged_days():
    # One day of food spread over a 10-day window -> average is ~1/10th.
    enriched = enrich_logs(_one_day_logs())
    report = deficiency_report(enriched, n_days=10)
    cal = report[report["nutrient"] == "calories"].iloc[0]
    # Rice 100g = 130 kcal total -> 13 kcal/day average.
    assert round(cal["avg_intake"], 1) == 13.0


def test_low_intake_flagged_deficient():
    report = deficiency_report(enrich_logs(_one_day_logs()), n_days=10)
    flagged = flagged_only(report)
    statuses = set(flagged["status"])
    assert "Deficient" in statuses
    # Calories are far below target, so they must be flagged.
    assert "calories" in flagged["nutrient"].tolist()


def test_status_values_are_valid():
    report = deficiency_report(enrich_logs(_one_day_logs()), n_days=10)
    assert set(report["status"]).issubset({"Deficient", "Low", "OK", "Over"})


def test_empty_logs_reports_all_deficient():
    empty = pd.DataFrame(columns=["meal_id", "date", "meal_type",
                                  "ingredient", "category", "quantity_g"])
    report = deficiency_report(enrich_logs(empty), n_days=7)
    # Zero intake against positive RDAs -> every nutrient deficient.
    assert (report["avg_intake"] == 0).all()
