"""Page 3 — flag nutrients where average daily intake falls short of targets."""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import bootstrap  # noqa: F401,E402

import streamlit as st  # noqa: E402

from db.repository import get_logs  # noqa: E402
from core.calories import enrich_logs  # noqa: E402
from core.deficiency import deficiency_report, flagged_only  # noqa: E402
from charts.visualize import rda_progress_bars  # noqa: E402

st.set_page_config(page_title="Deficiencies", page_icon="⚠️", layout="wide")
st.title("⚠️ Nutrition Deficiencies")

c1, c2 = st.columns(2)
start = c1.date_input("From", value=date.today() - timedelta(days=29))
end = c2.date_input("To", value=date.today())
if start > end:
    st.error("'From' must be on or before 'To'.")
    st.stop()

n_days = (end - start).days + 1
logs = get_logs(start, end)
if logs.empty:
    st.info("No meals logged in this range. Add some on the **Log Meal** page.")
    st.stop()

enriched = enrich_logs(logs)
report = deficiency_report(enriched, n_days)

st.caption(f"Average daily intake over {n_days} days "
           "(days with no log count as zero — this surfaces chronic shortfalls).")

flagged = flagged_only(report)
if flagged.empty:
    st.success("No deficiencies detected. Every tracked nutrient meets its target. 🎉")
else:
    deficient = flagged[flagged["status"] == "Deficient"]["nutrient"].tolist()
    low = flagged[flagged["status"] == "Low"]["nutrient"].tolist()
    if deficient:
        st.error("**Deficient (<70% of RDA):** " + ", ".join(deficient))
    if low:
        st.warning("**Low (70–90% of RDA):** " + ", ".join(low))

st.plotly_chart(rda_progress_bars(report), use_container_width=True)

st.subheader("Full breakdown")

# Strong fill + forced dark text so rows stay readable in light AND dark themes.
ROW_STYLE = {
    "Deficient": "background-color: #e74c3c; color: #ffffff; font-weight: 700;",
    "Low":       "background-color: #f39c12; color: #1a1a1a; font-weight: 700;",
    "OK":        "background-color: #2ecc71; color: #1a1a1a; font-weight: 700;",
}
STATUS_ICON = {"Deficient": "🔴 Deficient", "Low": "🟠 Low", "OK": "🟢 OK"}

display = report.copy()
display["status"] = display["status"].map(lambda s: STATUS_ICON.get(s, s))


def _style(row):
    key = row["status"].split(" ", 1)[-1]  # strip the emoji back off
    return [ROW_STYLE.get(key, "")] * len(row)


st.dataframe(
    display.style.apply(_style, axis=1),
    use_container_width=True, hide_index=True,
)

st.caption("Targets and thresholds are configurable in `config/settings.yaml`.")
