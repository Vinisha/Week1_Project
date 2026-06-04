"""Page 2 — calorie trends and ingredient-category amounts over any date range."""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import bootstrap  # noqa: F401,E402

import streamlit as st  # noqa: E402

from db.repository import get_logs  # noqa: E402
from core.calories import enrich_logs, daily_totals, period_totals  # noqa: E402
from core.ingredients import category_totals, daily_category_totals  # noqa: E402
from core.settings import NUTRIENTS, UNITS  # noqa: E402
from charts.visualize import (  # noqa: E402
    calorie_trend, calorie_period_bars, category_quantity_bars, category_trend,
)

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard")

# --- Date range picker --------------------------------------------------------
c1, c2, c3 = st.columns([1, 1, 1])
default_start = date.today() - timedelta(days=29)
start = c1.date_input("From", value=default_start)
end = c2.date_input("To", value=date.today())
agg = c3.selectbox("Long-range aggregation", ["week", "month"], index=0,
                   help="Used for the overview bar chart when you pick a wide range.")

if start > end:
    st.error("'From' must be on or before 'To'.")
    st.stop()

logs = get_logs(start, end)
if logs.empty:
    st.info("No meals logged in this range. Add some on the **Log Meal** page.")
    st.stop()

enriched = enrich_logs(logs)
daily = daily_totals(enriched)

# --- Headline metrics ---------------------------------------------------------
n_days = (end - start).days + 1
logged_days = daily["date"].nunique()
st.caption(f"{logged_days} of {n_days} days have logged meals.")
m = st.columns(4)
m[0].metric("Avg calories / day", f"{daily['calories'].sum() / max(n_days,1):.0f}")
m[1].metric("Avg protein / day", f"{daily['protein'].sum() / max(n_days,1):.0f} g")
m[2].metric("Total meals", int(logs['meal_id'].nunique()))
m[3].metric("Days logged", logged_days)

# --- Feature 2a: calories -----------------------------------------------------
st.subheader("Calories")
st.plotly_chart(calorie_trend(daily), use_container_width=True)
if n_days > 31:
    st.plotly_chart(
        calorie_period_bars(period_totals(enriched, by=agg), by=agg),
        use_container_width=True,
    )

# --- Feature 2b: ingredient amounts by category -------------------------------
st.subheader("Ingredient amounts by category")
cat_totals = category_totals(logs)
left, right = st.columns([1, 1])
with left:
    st.plotly_chart(category_quantity_bars(cat_totals), use_container_width=True)
with right:
    show = cat_totals.copy()
    show["total_kg"] = (show["quantity_g"] / 1000).round(2)
    st.dataframe(show, use_container_width=True, hide_index=True)

daily_cat = daily_category_totals(logs)
if not daily_cat.empty:
    st.plotly_chart(category_trend(daily_cat), use_container_width=True)

# --- Nutrient totals table ----------------------------------------------------
with st.expander("Nutrient totals for this range"):
    totals = {n: round(float(daily[n].sum()), 1) for n in NUTRIENTS}
    table = [{"nutrient": n, "total": totals[n], "unit": UNITS[n],
              "avg/day": round(totals[n] / max(n_days, 1), 1)} for n in NUTRIENTS]
    st.dataframe(table, use_container_width=True, hide_index=True)
