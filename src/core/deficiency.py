"""Compare average daily intake against RDA targets and flag deficiencies."""
import pandas as pd

from core.settings import NUTRIENTS, UNITS, load_settings
from core.calories import daily_totals


def deficiency_report(enriched: pd.DataFrame, n_days: int) -> pd.DataFrame:
    """Build a per-nutrient deficiency report over ``n_days`` calendar days.

    Intake is averaged across the full window (days with no log count as 0),
    which is the honest picture for spotting chronic shortfalls over time.

    Returns columns: nutrient, unit, avg_intake, rda, pct_of_rda, status.
    Status is one of: Deficient, Low, OK, Over (calories only).
    """
    settings = load_settings()
    rda = settings["rda"]
    def_thr = settings["deficiency_threshold"]
    low_thr = settings["low_threshold"]
    n_days = max(int(n_days), 1)

    daily = daily_totals(enriched)
    totals = {n: float(daily[n].sum()) if not daily.empty else 0.0 for n in NUTRIENTS}

    rows = []
    for n in NUTRIENTS:
        avg = totals[n] / n_days
        target = float(rda.get(n, 0)) or 0.0
        pct = (avg / target * 100.0) if target else 0.0
        if not target:
            status = "OK"
        elif pct < def_thr * 100:
            status = "Deficient"
        elif pct < low_thr * 100:
            status = "Low"
        else:
            status = "OK"
        rows.append(
            {
                "nutrient": n,
                "unit": UNITS.get(n, ""),
                "avg_intake": round(avg, 1),
                "rda": target,
                "pct_of_rda": round(pct, 1),
                "status": status,
            }
        )
    return pd.DataFrame(rows)


def flagged_only(report: pd.DataFrame) -> pd.DataFrame:
    """Subset of the report that needs attention (Deficient or Low)."""
    if report.empty:
        return report
    return report[report["status"].isin(["Deficient", "Low"])].reset_index(drop=True)
