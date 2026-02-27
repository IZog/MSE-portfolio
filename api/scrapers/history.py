"""Scrape historical price data from mse.mk/en/stats/symbolhistory/{ticker}."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.mse.mk/en/stats/symbolhistory/{ticker}"
_TIMEOUT = 25.0
_MAX_DAYS_PER_REQUEST = 365

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Number / date helpers
# ---------------------------------------------------------------------------

def _parse_number(text: str | None) -> float | None:
    """Parse a number that may use European or US formatting."""
    if not text:
        return None
    cleaned = text.strip().replace("%", "").replace("\xa0", "").replace(" ", "")
    if not cleaned or cleaned == "-" or cleaned.lower() in ("", "n/a"):
        return None

    # MSE English pages typically use "25,273.06" (US-style).
    # But some entries may have no decimal at all.
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        logger.debug("Cannot parse number: %r", text)
        return None


def _parse_int(text: str | None) -> int | None:
    val = _parse_number(text)
    return int(val) if val is not None else None


def _format_date(d: date) -> str:
    """Format a date as ``M/D/YYYY`` which is what the MSE query parameter expects."""
    return f"{d.month}/{d.day}/{d.year}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def scrape_history(
    ticker: str,
    days: int = 365,
) -> list[dict[str, Any]]:
    """Return historical price data for *ticker* covering the last *days* days.

    The MSE site limits each request to ~365 days, so for longer windows we
    issue multiple sequential requests and merge the results.
    """
    ticker = ticker.upper()
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    all_points: list[dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS, follow_redirects=True) as client:
        chunk_end = end_date
        while chunk_end > start_date:
            chunk_start = max(start_date, chunk_end - timedelta(days=_MAX_DAYS_PER_REQUEST))
            points = await _fetch_chunk(client, ticker, chunk_start, chunk_end)
            all_points.extend(points)
            # Move window backwards.
            chunk_end = chunk_start - timedelta(days=1)

    # Deduplicate by date (earlier chunks may overlap by a day).
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for p in all_points:
        if p["date"] not in seen:
            seen.add(p["date"])
            unique.append(p)

    # Sort oldest-first.
    unique.sort(key=lambda p: p["date"])
    return unique


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _fetch_chunk(
    client: httpx.AsyncClient,
    ticker: str,
    from_date: date,
    to_date: date,
) -> list[dict[str, Any]]:
    """Fetch a single chunk (max 365 days) of history."""
    url = _BASE_URL.format(ticker=ticker)
    params = {
        "FromDate": _format_date(from_date),
        "ToDate": _format_date(to_date),
    }
    logger.info("Fetching history for %s  %s -> %s", ticker, from_date, to_date)

    resp = await client.get(url, params=params)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    table = soup.find("table", id="resultsTable")
    if table is None:
        logger.warning("No resultsTable found for %s", ticker)
        return []

    rows = table.find_all("tr")  # type: ignore[union-attr]
    if len(rows) < 2:
        return []

    # Parse header to determine column order.
    header_cells = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
    col_map = _build_column_map(header_cells)

    points: list[dict[str, Any]] = []
    for tr in rows[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if not cells:
            continue
        point = _parse_row(cells, col_map)
        if point and point.get("date"):
            points.append(point)

    return points


def _build_column_map(headers: list[str]) -> dict[str, int]:
    """Map known column names to their index."""
    mapping: dict[str, int] = {}
    keywords = {
        "date": "date",
        "last trade price": "last_trade_price",
        "last": "last_trade_price",
        "max": "max_price",
        "min": "min_price",
        "avg": "avg_price",
        "%chg": "pct_change",
        "chg": "pct_change",
        "volume": "volume",
        "turnover in best": "turnover_best",
        "total turnover": "total_turnover",
    }
    for idx, header in enumerate(headers):
        for keyword, field in keywords.items():
            if keyword in header and field not in mapping:
                mapping[field] = idx
                break
    return mapping


def _parse_row(cells: list[str], col_map: dict[str, int]) -> dict[str, Any] | None:
    """Parse a single table row into a price-point dict."""
    if not cells:
        return None

    def _get(field: str) -> str | None:
        idx = col_map.get(field)
        if idx is not None and idx < len(cells):
            return cells[idx]
        return None

    return {
        "date": _get("date") or "",
        "last_trade_price": _parse_number(_get("last_trade_price")),
        "max_price": _parse_number(_get("max_price")),
        "min_price": _parse_number(_get("min_price")),
        "avg_price": _parse_number(_get("avg_price")),
        "pct_change": _parse_number(_get("pct_change")),
        "volume": _parse_int(_get("volume")),
        "turnover_best": _parse_number(_get("turnover_best")),
        "total_turnover": _parse_number(_get("total_turnover")),
    }
