"""Turn logged ingredients into calorie/nutrient totals by scaling per-100g values."""
import pandas as pd

from core.food_data import load_food_db
from core.settings import NUTRIENTS
from utils.dates import week_label, month_label


def enrich_logs(logs: pd.DataFrame) -> pd.DataFrame:
    """Join logged ingredients to the food DB and scale nutrients by quantity.

    Each nutrient column becomes the *absolute* amount contributed by that row
    (per-100g value * quantity_g / 100). Unknown ingredients contribute 0.
    """
    if logs.empty:
        return logs.assign(**{n: pd.Series(dtype="float") for n in NUTRIENTS})

    food = load_food_db().copy()
    food["_key"] = food["name"].str.lower()
    merged = logs.copy()
    merged["_key"] = merged["ingredient"].str.lower()
    merged = merged.merge(
        food[["_key"] + NUTRIENTS], on="_key", how="left"
    ).drop(columns="_key")

    factor = merged["quantity_g"].fillna(0) / 100.0
    for n in NUTRIENTS:
        merged[n] = merged[n].fillna(0) * factor
    return merged


def daily_totals(enriched: pd.DataFrame) -> pd.DataFrame:
    """Sum nutrients per day. Returns columns: date + every nutrient."""
    if enriched.empty:
        return pd.DataFrame(columns=["date"] + NUTRIENTS)
    return (
        enriched.groupby("date")[NUTRIENTS].sum().reset_index().sort_values("date")
    )


def period_totals(enriched: pd.DataFrame, by: str = "week") -> pd.DataFrame:
    """Aggregate nutrients per week or month — keeps a year+ of data readable.

    Returns columns: period (label) + every nutrient (summed) + ``days`` count.
    """
    if enriched.empty:
        return pd.DataFrame(columns=["period"] + NUTRIENTS + ["days"])
    labeller = week_label if by == "week" else month_label
    daily = daily_totals(enriched)
    daily["period"] = daily["date"].map(labeller)
    agg = daily.groupby("period")[NUTRIENTS].sum()
    agg["days"] = daily.groupby("period")["date"].nunique()
    return agg.reset_index().sort_values("period")
