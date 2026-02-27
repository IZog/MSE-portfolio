"""Macro-economic context: MBI10 index data plus static indicators."""

from __future__ import annotations

from typing import Any


def get_macro_context(mbi10_data: dict[str, Any]) -> dict[str, Any]:
    """Build the macro context dict from scraped MBI10 data and static values.

    Returns a dict matching the ``MacroContext`` schema.
    """
    return {
        "mbi10_value": mbi10_data.get("mbi10_value"),
        "mbi10_change_pct": mbi10_data.get("mbi10_change_pct"),
        # Static macroeconomic data for North Macedonia (update periodically).
        "gdp_growth": 3.2,
        "inflation": 3.2,
        "policy_rate": 5.35,
        "last_updated": "2026-02",
    }
