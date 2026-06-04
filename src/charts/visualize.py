"""Plotly figures for the dashboard and deficiency pages."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.settings import load_settings


def calorie_trend(daily: pd.DataFrame):
    """Line chart of daily calories with the acceptable band shaded."""
    settings = load_settings()
    lo = settings["calorie_range"]["min"]
    hi = settings["calorie_range"]["max"]

    fig = px.line(
        daily, x="date", y="calories", markers=True,
        title="Daily calorie intake", labels={"calories": "kcal", "date": "Date"},
    )
    fig.add_hrect(y0=lo, y1=hi, fillcolor="green", opacity=0.08, line_width=0,
                  annotation_text="target band", annotation_position="top left")
    fig.add_hline(y=settings["rda"]["calories"], line_dash="dash",
                  line_color="gray", annotation_text="RDA")
    return fig


def calorie_period_bars(period: pd.DataFrame, by: str = "week"):
    """Bar chart of total calories per week/month for long-range overviews."""
    fig = px.bar(
        period, x="period", y="calories",
        title=f"Calories per {by}", labels={"period": by.title(), "calories": "kcal"},
    )
    return fig


def category_quantity_bars(cat_totals: pd.DataFrame):
    """Bar chart of total grams consumed by ingredient category."""
    fig = px.bar(
        cat_totals, x="category", y="quantity_g", color="category",
        title="Amount used by category", labels={"quantity_g": "grams", "category": ""},
    )
    fig.update_layout(showlegend=False)
    return fig


def category_trend(daily_cat: pd.DataFrame):
    """Stacked area of daily grams per category over time."""
    fig = go.Figure()
    for col in daily_cat.columns:
        fig.add_trace(
            go.Scatter(x=daily_cat.index, y=daily_cat[col], name=col,
                       stackgroup="one", mode="lines")
        )
    fig.update_layout(title="Category amounts over time",
                      xaxis_title="Date", yaxis_title="grams")
    return fig


def rda_progress_bars(report: pd.DataFrame):
    """Horizontal bars of % of RDA met per nutrient, coloured by status."""
    color_map = {"Deficient": "#d62728", "Low": "#ff7f0e", "OK": "#2ca02c"}
    fig = px.bar(
        report, x="pct_of_rda", y="nutrient", orientation="h",
        color="status", color_discrete_map=color_map,
        title="% of RDA met (avg/day)",
        labels={"pct_of_rda": "% of RDA", "nutrient": ""},
    )
    fig.add_vline(x=100, line_dash="dash", line_color="gray")
    return fig
