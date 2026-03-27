"""Macro-economic context: MBI10 index data plus static indicators."""

from __future__ import annotations

from typing import Any


def get_macro_context(
    mbi10_data: dict[str, Any],
    mbi10_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the macro context dict from scraped MBI10 data and static values.

    Returns a dict matching the ``MacroContext`` schema.
    """
    mbi10_ytd_pct = _compute_mbi10_ytd(mbi10_history) if mbi10_history else None

    return {
        "mbi10_value": mbi10_data.get("mbi10_value"),
        "mbi10_change_pct": mbi10_data.get("mbi10_change_pct"),
        # Static macroeconomic data for North Macedonia (update periodically).
        "gdp_growth": 3.5,       # 2025 full-year GDP growth
        "inflation": 2.9,        # Feb 2026 annual CPI
        "policy_rate": 4.0,      # NBRM key rate (Mar 2026)
        "deposit_rate": 3.0,     # Estimated avg deposit rate
        "mbi10_ytd_pct": mbi10_ytd_pct,
        "last_updated": "2026-03",
    }


def _compute_mbi10_ytd(mbi10_history: list[dict[str, Any]]) -> float | None:
    """Compute year-to-date return % for MBI10."""
    if not mbi10_history:
        return None

    from datetime import date as _date

    current_year = _date.today().year
    ytd_start = None
    for p in mbi10_history:
        d = p.get("date", "")
        if d.startswith(str(current_year)):
            val = p.get("value")
            if val is not None:
                ytd_start = val
                break

    if ytd_start is None or ytd_start == 0:
        return None

    latest = None
    for p in reversed(mbi10_history):
        if p.get("value") is not None:
            latest = p["value"]
            break

    if latest is None:
        return None

    return round((latest - ytd_start) / ytd_start * 100, 2)
