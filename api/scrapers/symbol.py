"""Scrape company profile, financials, ratios, and price data from mse.mk."""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

BASE_URL = "https://www.mse.mk/en/symbol/{ticker}"

# Timeout for HTTP requests (seconds).
_TIMEOUT = 20.0

# Headers to mimic a real browser so the site doesn't reject us.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Number parsing helpers
# ---------------------------------------------------------------------------

def _parse_mkd_number(text: str | None) -> float | None:
    """Parse an MKD-formatted number string into a Python float.

    MSE uses the format ``25,273.06`` (commas as thousands separators,
    period for the decimal point).  Percentage signs are stripped.
    Returns ``None`` for empty / unparseable values.
    """
    if not text:
        return None
    cleaned = text.strip().replace("%", "").replace("\xa0", "").replace(" ", "")
    if not cleaned or cleaned == "-" or cleaned.lower() == "n/a":
        return None
    # Remove thousands-separator commas.
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        logger.debug("Could not parse number: %r", text)
        return None


def _parse_mkd_int(text: str | None) -> int | None:
    val = _parse_mkd_number(text)
    return int(val) if val is not None else None


# ---------------------------------------------------------------------------
# HTML extraction helpers
# ---------------------------------------------------------------------------

def _text(tag: Tag | None) -> str | None:
    """Return stripped text content of a tag, or None."""
    if tag is None:
        return None
    t = tag.get_text(strip=True)
    return t if t else None


def _find_label_value(soup: BeautifulSoup, label: str) -> str | None:
    """Find a value in a label-value pair layout common on MSE pages.

    Searches for a tag whose text matches *label* (case-insensitive) and
    returns the text of the next sibling ``<td>`` or ``<dd>`` element.
    """
    pattern = re.compile(re.escape(label), re.IGNORECASE)
    th = soup.find(string=pattern)
    if th is None:
        return None
    parent = th.find_parent(["th", "td", "dt", "strong", "span", "div"])
    if parent is None:
        return None

    # Try the next sibling <td> or <dd>.
    nxt = parent.find_next_sibling(["td", "dd"])
    if nxt:
        return _text(nxt)

    # Fallback: the next element at the same level.
    nxt = parent.find_next(["td", "dd", "span"])
    return _text(nxt) if nxt else None


def _extract_table_rows(table: Tag) -> list[list[str]]:
    """Return all rows of an HTML table as lists of cell text."""
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = [_text(td) or "" for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return rows


# ---------------------------------------------------------------------------
# Main scraper
# ---------------------------------------------------------------------------

async def scrape_symbol(ticker: str) -> dict[str, Any]:
    """Scrape the MSE symbol page for *ticker* and return structured data.

    Returns a dict with keys:
    - ``company``: company profile fields
    - ``price``: current price data
    - ``financials``: list of yearly financial data dicts
    - ``ratios``: financial ratio fields
    """
    url = BASE_URL.format(ticker=ticker.upper())
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # -- Company profile ------------------------------------------------
    company = _extract_company_profile(soup, ticker)

    # -- Price data -----------------------------------------------------
    price = _extract_price_data(soup)

    # -- Financials -----------------------------------------------------
    financials = _extract_financials(soup)

    # -- Ratios ---------------------------------------------------------
    ratios = _extract_ratios(soup)

    return {
        "company": company,
        "price": price,
        "financials": financials,
        "ratios": ratios,
    }


# ---------------------------------------------------------------------------
# Extraction sub-routines
# ---------------------------------------------------------------------------

def _extract_company_profile(soup: BeautifulSoup, ticker: str) -> dict[str, Any]:
    """Extract company name, description, address, and sector."""
    profile: dict[str, Any] = {"ticker": ticker.upper()}

    # Company name is usually in the page title or a prominent heading.
    title_tag = soup.find("title")
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        # Title is often "TICKER - Company Name | MSE"
        parts = title_text.split("-", 1)
        if len(parts) > 1:
            profile["name"] = parts[1].split("|")[0].strip()
        elif parts:
            profile["name"] = parts[0].strip()

    # Fallback: h1 or prominent heading with company name.
    if not profile.get("name"):
        h1 = soup.find("h1")
        if h1:
            profile["name"] = _text(h1)

    # Description - look for "About" section or similar.
    about_section = soup.find(string=re.compile(r"About|Description|Profile", re.I))
    if about_section:
        parent = about_section.find_parent(["div", "section", "td"])
        if parent:
            p_tag = parent.find("p")
            if p_tag:
                profile["description"] = _text(p_tag)

    # Address
    profile["address"] = _find_label_value(soup, "Address")

    # Sector
    profile["sector"] = _find_label_value(soup, "Sector")

    return profile


def _extract_price_data(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract current price, 52-week range, shares outstanding, market cap."""
    price: dict[str, Any] = {}

    # Current price — MSE uses <span class="price"> inside the symbol header.
    price_el = soup.find("span", class_="price")
    if price_el:
        price["current_price"] = _parse_mkd_number(_text(price_el))

    # Fallback: look for label-based price.
    if not price.get("current_price"):
        for label in ("Last trade price", "Price", "Last Price", "Closing Price"):
            val = _find_label_value(soup, label)
            if val:
                price["current_price"] = _parse_mkd_number(val)
                break

    # Price change % — MSE uses <span class="change-percent">.
    chg_el = soup.find("span", class_="change-percent")
    if chg_el:
        price["price_change_pct"] = _parse_mkd_number(_text(chg_el))
    else:
        chg = _find_label_value(soup, "%chg") or _find_label_value(soup, "Change")
        price["price_change_pct"] = _parse_mkd_number(chg)

    # 52-week high / low — MSE labels these as "Max Price" and "Min Price"
    # inside the "Last 52 weeks" section.
    for label in ("Max Price", "52 week high", "52-week high"):
        val = _find_label_value(soup, label)
        if val:
            price["high_52w"] = _parse_mkd_number(val)
            break
    for label in ("Min Price", "52 week low", "52-week low"):
        val = _find_label_value(soup, label)
        if val:
            price["low_52w"] = _parse_mkd_number(val)
            break

    # Total shares outstanding
    for label in ("Total shares", "Shares outstanding", "Number of shares"):
        val = _find_label_value(soup, label)
        if val:
            price["total_shares"] = _parse_mkd_int(val)
            break

    # Market capitalisation
    price["market_cap"] = _parse_mkd_number(
        _find_label_value(soup, "Market capitali")
    )

    return price


def _extract_financials(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Extract multi-year financial data from tables on the symbol page."""
    financials: list[dict[str, Any]] = []

    # Financial tables often have headings like "Income Statement", "Balance Sheet".
    # We look for tables near these headings and parse them.
    financial_labels = {
        "revenue": re.compile(r"revenue|sales|income from operations", re.I),
        "operating_profit": re.compile(r"operating profit|operating income|EBIT", re.I),
        "net_profit": re.compile(r"net profit|net income|profit after tax", re.I),
        "equity": re.compile(r"equity|shareholders.*equity|net worth", re.I),
        "total_assets": re.compile(r"total assets", re.I),
        "total_liabilities": re.compile(r"total liabilities", re.I),
    }

    # Strategy: find all tables, check if they have year headers and known row labels.
    tables = soup.find_all("table")
    for table in tables:
        rows = _extract_table_rows(table)
        if len(rows) < 2:
            continue

        # Try to identify year columns from the header row.
        header = rows[0]
        year_indices: dict[int, int] = {}  # col_index -> year
        for idx, cell in enumerate(header):
            match = re.search(r"(20\d{2})", cell)
            if match:
                year_indices[idx] = int(match.group(1))

        if not year_indices:
            continue

        # Build a per-year dict by matching row labels.
        year_data: dict[int, dict[str, float | None]] = {
            y: {} for y in year_indices.values()
        }

        for row in rows[1:]:
            if not row:
                continue
            label = row[0]
            for field, pattern in financial_labels.items():
                if pattern.search(label):
                    for col_idx, year in year_indices.items():
                        if col_idx < len(row):
                            year_data[year][field] = _parse_mkd_number(row[col_idx])
                    break

        for year in sorted(year_data):
            data = year_data[year]
            if any(v is not None for v in data.values()):
                financials.append({"year": year, **data})

    return financials


def _extract_ratios(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract key financial ratios from the symbol page."""
    ratios: dict[str, Any] = {}

    mapping = {
        "pe_ratio": ["P/E", "Price/Earnings", "PE Ratio"],
        "eps": ["EPS", "Earnings per share"],
        "roa": ["ROA", "Return on assets"],
        "roe": ["ROE", "Return on equity"],
        "book_value_per_share": ["Book value per share", "BV per share"],
        "dividend_per_share": ["Dividend per share", "DPS"],
        "dividend_yield": ["Dividend yield"],
        "market_cap": ["Market capitali"],
    }

    for key, labels in mapping.items():
        for label in labels:
            val = _find_label_value(soup, label)
            if val is not None:
                ratios[key] = _parse_mkd_number(val)
                break

    return ratios
