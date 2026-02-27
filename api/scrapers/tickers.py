"""Scrape the list of traded equity tickers from mse.mk."""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_URL = "https://www.mse.mk/en/stats/current-schedule"
_TIMEOUT = 20.0

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Pattern to detect bond ISINs (typically start with MKMINF or contain "bond" in name).
_BOND_PATTERN = re.compile(r"bond|obligac|obveznic", re.IGNORECASE)


async def scrape_tickers() -> list[dict[str, Any]]:
    """Return a list of equity ticker dicts from the MSE current-schedule page.

    Each dict has keys: ``symbol``, ``name``, ``isin``, ``market_segment``.
    Bonds and non-equity instruments are filtered out.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS, follow_redirects=True) as client:
        resp = await client.get(_URL)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    tickers: list[dict[str, Any]] = []

    # The page contains one or more tables grouped by market segment.
    tables = soup.find_all("table")
    for table in tables:
        segment = _detect_segment(table)
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        # Determine column positions from header.
        header_cells = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
        col = _column_indices(header_cells)

        for tr in rows[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if not cells:
                continue

            symbol = _safe_get(cells, col.get("symbol"))
            name = _safe_get(cells, col.get("name"))
            isin = _safe_get(cells, col.get("isin"))

            if not symbol:
                continue

            # Filter out bonds.
            if _is_bond(symbol, name, isin):
                continue

            tickers.append({
                "symbol": symbol,
                "name": name,
                "isin": isin,
                "market_segment": segment,
            })

    # Deduplicate by symbol.
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for t in tickers:
        if t["symbol"] not in seen:
            seen.add(t["symbol"])
            unique.append(t)

    logger.info("Scraped %d equity tickers", len(unique))
    return unique


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_segment(table) -> str | None:
    """Try to find a market-segment heading immediately before *table*."""
    prev = table.find_previous(["h2", "h3", "h4", "strong"])
    if prev:
        return prev.get_text(strip=True)
    return None


def _column_indices(headers: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    keywords = {
        "code": "symbol",
        "symbol": "symbol",
        "ticker": "symbol",
        "name": "name",
        "issuer": "name",
        "company": "name",
        "isin": "isin",
        "segment": "segment",
        "market": "segment",
    }
    for idx, h in enumerate(headers):
        for kw, field in keywords.items():
            if kw in h and field not in mapping:
                mapping[field] = idx
                break
    return mapping


def _safe_get(cells: list[str], idx: int | None) -> str | None:
    if idx is not None and idx < len(cells):
        val = cells[idx].strip()
        return val if val else None
    return None


def _is_bond(symbol: str, name: str | None, isin: str | None) -> bool:
    """Heuristic filter: return True if the instrument is likely a bond."""
    if _BOND_PATTERN.search(symbol):
        return True
    if name and _BOND_PATTERN.search(name):
        return True
    if isin and isin.startswith("MKMINF"):
        return True
    return False
