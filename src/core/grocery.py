"""Build a weekly grocery list by aggregating the ingredients actually logged."""
import pandas as pd

from utils.dates import week_bounds


def grocery_list_for_week(logs: pd.DataFrame) -> pd.DataFrame:
    """Consolidate a week's logged ingredients into a shopping list.

    Sums the same ingredient across every meal in the range and reports the
    total grams to buy. Returns columns: category, ingredient, total_g, total_kg.
    Caller is expected to pass logs already filtered to the target week.
    """
    if logs.empty:
        return pd.DataFrame(columns=["category", "ingredient", "total_g", "total_kg"])

    grouped = (
        logs.groupby(["category", "ingredient"])["quantity_g"].sum().reset_index()
        .rename(columns={"quantity_g": "total_g"})
    )
    grouped["total_kg"] = (grouped["total_g"] / 1000.0).round(3)
    grouped["total_g"] = grouped["total_g"].round(1)
    return grouped.sort_values(["category", "ingredient"]).reset_index(drop=True)


def to_text(grocery: pd.DataFrame, week_start, week_end) -> str:
    """Render the grocery list as a plain-text checklist grouped by category."""
    lines = [f"Grocery list  ({week_start} to {week_end})", "=" * 40]
    if grocery.empty:
        lines.append("(no meals logged this week)")
        return "\n".join(lines)
    for category, block in grocery.groupby("category"):
        lines.append(f"\n{category.upper()}")
        for _, row in block.iterrows():
            qty = (
                f"{row['total_kg']} kg" if row["total_g"] >= 1000
                else f"{int(round(row['total_g']))} g"
            )
            lines.append(f"  [ ] {row['ingredient']:<20} {qty}")
    return "\n".join(lines)


def week_for(d) -> tuple:
    """Convenience re-export so pages can get week bounds from one place."""
    return week_bounds(d)
