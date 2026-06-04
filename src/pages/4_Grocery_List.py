"""Page 4 — weekly grocery list built from the meals logged that week."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import bootstrap  # noqa: F401,E402

import streamlit as st  # noqa: E402

from db.repository import get_logs  # noqa: E402
from core.grocery import grocery_list_for_week, to_text  # noqa: E402
from utils.dates import week_bounds  # noqa: E402
from utils.paths import EXPORTS_DIR  # noqa: E402

st.set_page_config(page_title="Grocery List", page_icon="🛒", layout="wide")
st.title("🛒 Weekly Grocery List")
st.caption("Aggregates the ingredients you logged during the selected week into a "
           "single shopping list — handy for repeating a week you ate well.")

picked = st.date_input("Pick any day in the target week", value=date.today())
week_start, week_end = week_bounds(picked)
st.write(f"**Week:** {week_start} → {week_end} (Mon–Sun)")

logs = get_logs(week_start, week_end)
grocery = grocery_list_for_week(logs)

if grocery.empty:
    st.info("No meals logged for this week. Log meals first, then come back.")
    st.stop()

# A distinct colour per food category, used for both the header and the rows.
CATEGORY_COLORS = {
    "vegetable": "#2ecc71",
    "lentil":    "#e67e22",
    "non-veg":   "#e74c3c",
    "grain":     "#d4ac0d",
    "dairy":     "#3498db",
    "fruit":     "#9b59b6",
    "fat-oil":   "#16a085",
    "other":     "#7f8c8d",
}
CATEGORY_ICON = {
    "vegetable": "🥬", "lentil": "🫘", "non-veg": "🍗", "grain": "🌾",
    "dairy": "🥛", "fruit": "🍎", "fat-oil": "🫒", "other": "🥄",
}

for category, block in grocery.groupby("category"):
    color = CATEGORY_COLORS.get(category, "#444444")
    icon = CATEGORY_ICON.get(category, "•")
    st.markdown(
        f"<h4 style='color:{color}; margin-bottom:0.2rem'>"
        f"{icon} {category.title()}</h4>",
        unsafe_allow_html=True,
    )
    styled = (
        block[["ingredient", "total_g", "total_kg"]]
        .style.set_properties(
            subset=["ingredient"],
            **{"color": color, "font-weight": "700"},
        )
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

total_kg = grocery["total_kg"].sum()
st.metric("Total to buy", f"{total_kg:.2f} kg across {len(grocery)} items")

# --- Export -------------------------------------------------------------------
text = to_text(grocery, week_start, week_end)
st.download_button(
    "⬇️ Download checklist (.txt)", data=text,
    file_name=f"grocery_{week_start}_{week_end}.txt", mime="text/plain",
)
st.download_button(
    "⬇️ Download as CSV", data=grocery.to_csv(index=False),
    file_name=f"grocery_{week_start}_{week_end}.csv", mime="text/csv",
)

if st.button("💾 Save checklist to exports/ folder"):
    path = os.path.join(EXPORTS_DIR, f"grocery_{week_start}_{week_end}.txt")
    with open(path, "w") as f:
        f.write(text)
    st.success(f"Saved to {path}")

with st.expander("Preview text checklist"):
    st.code(text)
