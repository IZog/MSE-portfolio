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

    MSE uses several layouts:
    1. <th>Label</th><td>Value</td>   (financial tables)
    2. <div class="col-md-5">Label</div><div class="col-md-7">Value</div>
    3. <div class="row">Label:Value</div>
    """
    pattern = re.compile(re.escape(label), re.IGNORECASE)
    th = soup.find(string=pattern)
    if th is None:
        return None
    parent = th.find_parent(["th", "td", "dt", "strong", "span", "div"])
    if parent is None:
        return None

    # Try the next sibling <td> or <dd> (table layout).
    nxt = parent.find_next_sibling(["td", "dd"])
    if nxt:
        return _text(nxt)

    # Try the next sibling <div> (Bootstrap col layout).
    nxt_div = parent.find_next_sibling("div")
    if nxt_div:
        return _text(nxt_div)

    # Fallback: the next element at the same level.
    nxt = parent.find_next(["td", "dd", "span", "div"])
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

    # Company name from page title: "TICKER - Company Name | MSE"
    title_tag = soup.find("title")
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        parts = title_text.split("-", 1)
        if len(parts) > 1:
            profile["name"] = parts[1].split("|")[0].strip()
        elif parts:
            profile["name"] = parts[0].strip()

    # Fallback: h1.
    if not profile.get("name"):
        h1 = soup.find("h1")
        if h1:
            profile["name"] = _text(h1)

    # Description from the #companyProfile tab pane.
    cp_div = soup.find(id="companyProfile")
    if cp_div:
        p_tag = cp_div.find("p")
        if p_tag:
            profile["description"] = _text(p_tag)

    # Sector / market segment (e.g. "Exchange Listing - Ordinary shares").
    profile["sector"] = _find_label_value(soup, "Market segment")

    # Address — not reliably available on the symbol page; skip to avoid
    # pulling wrong data (e.g. "Contact person" label).
    profile["address"] = None

    return profile


def _extract_section_rows(soup: BeautifulSoup, header_text: str) -> dict[str, str]:
    """Extract key:value pairs from div.row elements following a section header.

    MSE uses a pattern like:
        <div class="row"><div class="col well-minimal">Last trade: ...</div></div>
        <div class="row">Max Price:25,300.00</div>
        <div class="row">Min Price:25,200.00</div>
        ...
    """
    result: dict[str, str] = {}
    header_el = soup.find(string=lambda s: s and header_text in str(s))
    if not header_el:
        return result
    row_div = header_el.find_parent("div", class_="row")
    if not row_div:
        return result
    for sib in row_div.find_next_siblings("div", class_="row"):
        text = sib.get_text(strip=True)
        # Stop if we hit the next section header (text without a colon-number pattern).
        if ":" not in text:
            break
        # Also stop if we hit another well-known section header.
        if any(h in text for h in ("Last 52 weeks", "Last trade", "*")):
            break
        parts = text.split(":", 1)
        if len(parts) == 2:
            result[parts[0].strip()] = parts[1].strip()
    return result


def _extract_price_data(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract current price, 52-week range, shares outstanding, market cap."""
    price: dict[str, Any] = {}

    # --- "Last trade" section gives current-day price data ---
    last_trade = _extract_section_rows(soup, "Last trade")
    if last_trade.get("Avg Price"):
        price["current_price"] = _parse_mkd_number(last_trade["Avg Price"])

    # --- "Last 52 weeks" section gives yearly high/low ---
    last_52w = _extract_section_rows(soup, "Last 52 weeks")
    price["high_52w"] = _parse_mkd_number(last_52w.get("Max Price"))
    price["low_52w"] = _parse_mkd_number(last_52w.get("Min Price"))

    # Price change % — derive from last_trade vs previous if available,
    # otherwise look for a percentage in the page header ticker strip.
    # The MSE ticker strip shows e.g. "ALK 25,273.06 0.92 %" as link text.
    if not price.get("price_change_pct"):
        for a_tag in soup.find_all("a", href=re.compile(r"/en/symbol/", re.I)):
            link_text = a_tag.get_text(strip=True)
            pct_match = re.search(r"(-?\d+[\.,]?\d*)\s*%", link_text)
            ticker_match = re.search(r"^[A-Z]{2,5}", link_text)
            if pct_match and ticker_match:
                # Only use if it matches our ticker.
                if link_text.startswith(soup.find("title").get_text(strip=True).split("-")[0].strip()[:3]):
                    price["price_change_pct"] = _parse_mkd_number(pct_match.group(1))
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
                # Skip rows that look like percentages (values < 100 when
                # we expect figures in thousands of MKD).
                revenue = data.get("revenue")
                if revenue is not None and abs(revenue) < 100:
                    continue
                financials.append({"year": year, **data})

    # Deduplicate by year — keep the entry with the most fields.
    seen: dict[int, dict] = {}
    for entry in financials:
        yr = entry["year"]
        if yr not in seen or sum(1 for v in entry.values() if v is not None) > sum(
            1 for v in seen[yr].values() if v is not None
        ):
            seen[yr] = entry
    return sorted(seen.values(), key=lambda d: d["year"])


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
