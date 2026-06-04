"""Aggregate ingredient quantities by category (vegetable / lentil / non-veg / ...)."""
import pandas as pd


def category_totals(logs: pd.DataFrame) -> pd.DataFrame:
    """Total grams consumed per category over the whole range.

    Returns columns: category, quantity_g (sorted high to low).
    """
    if logs.empty:
        return pd.DataFrame(columns=["category", "quantity_g"])
    out = (
        logs.groupby("category")["quantity_g"].sum().reset_index()
        .sort_values("quantity_g", ascending=False)
    )
    return out


def daily_category_totals(logs: pd.DataFrame) -> pd.DataFrame:
    """Grams per category per day — wide table (date as index, category columns)."""
    if logs.empty:
        return pd.DataFrame()
    pivot = (
        logs.groupby(["date", "category"])["quantity_g"].sum()
        .unstack(fill_value=0)
        .sort_index()
    )
    return pivot
