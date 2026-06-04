"""Page 1 — log a meal with its ingredients, and review/delete recent meals."""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import bootstrap  # noqa: F401,E402

import streamlit as st  # noqa: E402

from core.food_data import load_food_db, food_names, lookup, add_food  # noqa: E402
from core.settings import NUTRIENTS, UNITS, get_categories  # noqa: E402
from db.repository import add_meal, get_meals_summary, get_logs, delete_meal  # noqa: E402

st.set_page_config(page_title="Log Meal", page_icon="📝", layout="wide")
st.title("📝 Log a Meal")

MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]

# --- Session state for the ingredient line items being built up ---------------
if "lines" not in st.session_state:
    st.session_state.lines = []

col_form, col_review = st.columns([1, 1])

with col_form:
    st.subheader("1. Meal details")
    meal_date = st.date_input("Date", value=date.today(), max_value=date.today())
    meal_type = st.selectbox("Meal", MEAL_TYPES)
    notes = st.text_input("Notes (optional)", placeholder="e.g. post-workout")

    st.subheader("2. Add ingredients")
    names = food_names()
    pick = st.selectbox("Ingredient", names, index=0 if names else None,
                        help="Not listed? Add it under 'New ingredient' below.")
    qty = st.number_input("Quantity (grams)", min_value=1.0, value=100.0, step=10.0)
    if st.button("➕ Add ingredient", use_container_width=True):
        food = lookup(pick)
        if food:
            st.session_state.lines.append(
                {"ingredient": food["name"], "category": food["category"],
                 "quantity_g": float(qty)}
            )
            st.rerun()

    with st.expander("New ingredient (adds to your food database)"):
        new_name = st.text_input("Name", key="nf_name")
        new_cat = st.selectbox("Category", get_categories(), key="nf_cat")
        st.caption("Nutrient values are per 100 g.")
        vals = {}
        ncols = st.columns(3)
        for i, n in enumerate(NUTRIENTS):
            vals[n] = ncols[i % 3].number_input(
                f"{n} ({UNITS[n]})", min_value=0.0, value=0.0, key=f"nf_{n}")
        if st.button("Save new ingredient"):
            if new_name.strip():
                add_food(new_name, new_cat, vals)
                st.success(f"Added '{new_name.strip()}' to the food database.")
                st.rerun()
            else:
                st.warning("Give the ingredient a name first.")

with col_review:
    st.subheader("3. This meal so far")
    if not st.session_state.lines:
        st.info("No ingredients added yet.")
    else:
        st.dataframe(st.session_state.lines, use_container_width=True, hide_index=True)
        if st.button("Clear list"):
            st.session_state.lines = []
            st.rerun()
        if st.button("✅ Save meal", type="primary", use_container_width=True):
            add_meal(meal_date, meal_type, st.session_state.lines, notes)
            st.session_state.lines = []
            st.success(f"Saved {meal_type} for {meal_date}.")
            st.rerun()

st.divider()

# --- Recent meals (last 30 days) ---------------------------------------------
st.subheader("Recent meals")
recent = get_meals_summary(date.today() - timedelta(days=30), date.today())
if recent.empty:
    st.caption("Nothing logged in the last 30 days.")
else:
    st.dataframe(recent, use_container_width=True, hide_index=True)
    to_delete = st.selectbox("Delete a meal by id", [""] + recent["meal_id"].tolist())
    if to_delete != "" and st.button("🗑️ Delete selected meal"):
        delete_meal(int(to_delete))
        st.success(f"Deleted meal #{to_delete}.")
        st.rerun()
