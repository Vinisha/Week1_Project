"""Date helpers for weekly/monthly aggregation across long time ranges."""
from datetime import date, timedelta


def week_bounds(d: date):
    """Return (Monday, Sunday) of the ISO week containing ``d``."""
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def week_label(d: date) -> str:
    """ISO-year/week label, e.g. '2026-W23' — stable for grouping a year+ of data."""
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def month_label(d: date) -> str:
    return d.strftime("%Y-%m")


def daterange(start: date, end: date):
    """Yield each date from ``start`` to ``end`` inclusive."""
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)
