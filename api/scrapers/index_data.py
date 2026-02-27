"""Scrape MBI10 index data from the MSE website."""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_MSE_HOME = "https://www.mse.mk/en"
_MBI10_SYMBOL = "https://www.mse.mk/en/symbol/MBI10"
_TIMEOUT = 20.0

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
    cleaned = text.strip().replace("%", "").replace("\xa0", "").replace(" ", "").replace(",", "")
    if not cleaned or cleaned == "-" or cleaned.lower() == "n/a":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


async def scrape_mbi10() -> dict[str, Any]:
    """Return MBI10 index value and daily change percentage.

    Tries the MSE homepage first, then falls back to the MBI10 symbol page.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS, follow_redirects=True) as client:
        # Try homepage first - it typically shows index values.
        result = await _try_homepage(client)
        if result.get("mbi10_value") is not None:
            return result

        # Fallback: MBI10 symbol page.
        result = await _try_symbol_page(client)
        return result


async def _try_homepage(client: httpx.AsyncClient) -> dict[str, Any]:
    """Extract MBI10 data from the MSE homepage."""
    try:
        resp = await client.get(_MSE_HOME)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Failed to fetch MSE homepage: %s", exc)
        return {}

    soup = BeautifulSoup(resp.text, "lxml")
    result: dict[str, Any] = {}

    # The homepage usually shows MBI10 in a prominent panel / widget.
    mbi_el = soup.find(string=re.compile(r"MBI[\s-]*10", re.I))
    if mbi_el:
        parent = mbi_el.find_parent(["div", "tr", "td", "section"])
        if parent:
            numbers = re.findall(r"-?[\d,]+\.?\d*", parent.get_text())
            if numbers:
                result["mbi10_value"] = _parse_number(numbers[0])
            if len(numbers) > 1:
                result["mbi10_change_pct"] = _parse_number(numbers[1])

    return result


async def _try_symbol_page(client: httpx.AsyncClient) -> dict[str, Any]:
    """Extract MBI10 data from the dedicated symbol page."""
    result: dict[str, Any] = {}
    try:
        resp = await client.get(_MBI10_SYMBOL)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Failed to fetch MBI10 symbol page: %s", exc)
        return result

    soup = BeautifulSoup(resp.text, "lxml")

    # Look for last trade price / value.
    for label in ("Last trade price", "Value", "Price", "Index Value"):
        tag = soup.find(string=re.compile(re.escape(label), re.I))
        if tag:
            parent = tag.find_parent(["th", "td", "dt", "strong", "span", "div"])
            if parent:
                nxt = parent.find_next(["td", "dd", "span"])
                if nxt:
                    result["mbi10_value"] = _parse_number(nxt.get_text(strip=True))
                    break

    # Change %
    for label in ("%chg", "Change"):
        tag = soup.find(string=re.compile(re.escape(label), re.I))
        if tag:
            parent = tag.find_parent(["th", "td", "dt", "strong", "span", "div"])
            if parent:
                nxt = parent.find_next(["td", "dd", "span"])
                if nxt:
                    result["mbi10_change_pct"] = _parse_number(nxt.get_text(strip=True))
                    break

    return result
