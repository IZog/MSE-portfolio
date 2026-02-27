"""Scrape historical MBI10 index data from mse.mk."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.mse.mk/en/stats/symbolhistory/MBI10"
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


def _parse_number(text: str | None) -> float | None:
    if not text:
        return None
    cleaned = text.strip().replace("%", "").replace("\xa0", "").replace(" ", "")
    if not cleaned or cleaned == "-" or cleaned.lower() in ("", "n/a"):
        return None
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _format_date(d: date) -> str:
    return f"{d.month}/{d.day}/{d.year}"


async def scrape_index_history(days: int = 365) -> list[dict[str, Any]]:
    """Return historical MBI10 index data for the last *days* days."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    all_points: list[dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS, follow_redirects=True) as client:
        chunk_end = end_date
        while chunk_end > start_date:
            chunk_start = max(start_date, chunk_end - timedelta(days=_MAX_DAYS_PER_REQUEST))
            points = await _fetch_chunk(client, chunk_start, chunk_end)
            all_points.extend(points)
            chunk_end = chunk_start - timedelta(days=1)

    # Deduplicate by date.
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for p in all_points:
        if p["date"] not in seen:
            seen.add(p["date"])
            unique.append(p)

    unique.sort(key=lambda p: p["date"])
    return unique


async def _fetch_chunk(
    client: httpx.AsyncClient,
    from_date: date,
    to_date: date,
) -> list[dict[str, Any]]:
    """Fetch a single chunk of MBI10 history."""
    params = {
        "FromDate": _format_date(from_date),
        "ToDate": _format_date(to_date),
    }
    logger.info("Fetching MBI10 history %s -> %s", from_date, to_date)

    resp = await client.get(_BASE_URL, params=params)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    table = soup.find("table", id="resultsTable")
    if table is None:
        logger.warning("No resultsTable found for MBI10")
        return []

    rows = table.find_all("tr")
    if len(rows) < 2:
        return []

    # Parse header.
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
    mapping: dict[str, int] = {}
    keywords = {
        "date": "date",
        "last trade price": "value",
        "last": "value",
        "avg": "value",
        "%chg": "pct_change",
        "chg": "pct_change",
        "volume": "volume",
        "turnover in best": "turnover",
        "total turnover": "turnover",
    }
    for idx, header in enumerate(headers):
        for keyword, field in keywords.items():
            if keyword in header and field not in mapping:
                mapping[field] = idx
                break
    return mapping


def _parse_row(cells: list[str], col_map: dict[str, int]) -> dict[str, Any] | None:
    if not cells:
        return None

    def _get(field: str) -> str | None:
        idx = col_map.get(field)
        if idx is not None and idx < len(cells):
            return cells[idx]
        return None

    return {
        "date": _get("date") or "",
        "value": _parse_number(_get("value")),
        "pct_change": _parse_number(_get("pct_change")),
        "volume": _parse_number(_get("volume")),
        "turnover": _parse_number(_get("turnover")),
    }
