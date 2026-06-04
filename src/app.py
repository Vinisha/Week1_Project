"""Nutrition Tracker — local Streamlit app.

Run from the project root:
    streamlit run src/app.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # put src on the path
import bootstrap  # noqa: F401,E402  (sets up path + initialises the database)

import streamlit as st  # noqa: E402

from core.settings import load_settings  # noqa: E402

st.set_page_config(page_title="Nutrition Tracker", page_icon="🥗", layout="wide")

settings = load_settings()
profile = settings.get("profile", {})

st.title("🥗 Nutrition Tracker")
st.caption(f"Local nutrition tracking for **{profile.get('name', 'you')}** — "
           "built to follow your meals over a year and beyond.")

st.markdown(
    """
Use the pages in the sidebar:

1. **Log Meal** — record daily meals, their ingredients and quantities.
2. **Dashboard** — calorie trends and how much veg / lentils / non-veg etc. you used.
3. **Deficiencies** — see where your intake falls short of your daily targets.
4. **Grocery List** — a shopping list built from a week of logged meals.

---
#### Your daily targets (RDA)
Edit these any time in `config/settings.yaml`.
    """
)

rda = settings["rda"]
cols = st.columns(len(rda))
from core.settings import UNITS  # noqa: E402
for col, (k, v) in zip(cols, rda.items()):
    col.metric(k.replace("_", " ").title(), f"{v} {UNITS.get(k, '')}")

st.info("New here? Start with **Log Meal**, then check the **Dashboard**.", icon="👉")
