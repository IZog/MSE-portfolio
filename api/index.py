"""MSE Research Dashboard API -- FastAPI application with all routes."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.models.schemas import (
    CompanyProfile,
    FinancialData,
    FinancialRatios,
    MacroContext,
    PriceData,
    PricePoint,
    ResearchReport,
    RiskAssessment,
    TechnicalAnalysis,
    TickerInfo,
    ValuationMetrics,
    Verdict,
)
from api.scrapers.history import scrape_history
from api.scrapers.index_data import scrape_mbi10
from api.scrapers.symbol import scrape_symbol
from api.scrapers.tickers import scrape_tickers
from api.analysis.valuation import compute_valuation
from api.analysis.technical import compute_technical
from api.analysis.risk import assess_risk
from api.analysis.macro import get_macro_context
from api.analysis.verdict import generate_verdict

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="MSE Research Dashboard API",
    version="1.0.0",
    description="Backend API for the Macedonian Stock Exchange research dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

_ticker_cache: dict[str, Any] = {"data": None, "fetched_at": 0.0}
_TICKER_CACHE_TTL = 3600  # seconds (1 hour)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/health")
async def health():
    """Simple health-check endpoint."""
    return {"status": "ok", "timestamp": _now_iso()}


@app.get("/api/tickers", response_model=list[TickerInfo])
async def get_tickers():
    """Return all listed equity tickers from the MSE trading schedule.

    Results are cached for 1 hour to avoid hammering the MSE site.
    """
    now = time.time()
    if (
        _ticker_cache["data"] is not None
        and (now - _ticker_cache["fetched_at"]) < _TICKER_CACHE_TTL
    ):
        return _ticker_cache["data"]

    try:
        raw = await scrape_tickers()
    except Exception as exc:
        logger.error("Failed to scrape tickers: %s", exc)
        if _ticker_cache["data"] is not None:
            # Serve stale data rather than erroring out.
            return _ticker_cache["data"]
        raise HTTPException(status_code=502, detail="Could not fetch ticker list from MSE")

    tickers = [TickerInfo(**t) for t in raw]
    _ticker_cache["data"] = tickers
    _ticker_cache["fetched_at"] = now
    return tickers


@app.get("/api/research/{ticker}", response_model=ResearchReport)
async def get_research(
    ticker: str,
    days: int = Query(default=365, ge=7, le=3650, description="Days of price history"),
):
    """Generate a full research report for the given ticker.

    Scrapes company data and price history concurrently, then runs the
    analysis pipeline (valuation, technical, risk, macro, verdict).
    """
    ticker = ticker.upper()
    logger.info("Generating research report for %s (days=%d)", ticker, days)

    # ---- Step 1: Scrape data concurrently ----------------------------
    try:
        symbol_task = asyncio.create_task(scrape_symbol(ticker))
        history_task = asyncio.create_task(scrape_history(ticker, days=days))
        mbi10_task = asyncio.create_task(scrape_mbi10())

        symbol_data, history_data, mbi10_data = await asyncio.gather(
            symbol_task, history_task, mbi10_task,
            return_exceptions=True,
        )
    except Exception as exc:
        logger.error("Scraping failed for %s: %s", ticker, exc)
        raise HTTPException(status_code=502, detail=f"Failed to scrape data for {ticker}")

    # Handle individual scraper failures gracefully.
    if isinstance(symbol_data, BaseException):
        logger.error("Symbol scraper failed: %s", symbol_data)
        raise HTTPException(
            status_code=502,
            detail=f"Could not fetch symbol page for {ticker}. The ticker may not exist.",
        )

    if isinstance(history_data, BaseException):
        logger.warning("History scraper failed: %s", history_data)
        history_data = []

    if isinstance(mbi10_data, BaseException):
        logger.warning("MBI10 scraper failed: %s", mbi10_data)
        mbi10_data = {}

    # ---- Step 2: Unpack scraped data ---------------------------------
    company_raw = symbol_data.get("company", {})
    price_raw = symbol_data.get("price", {})
    financials_raw = symbol_data.get("financials", [])
    ratios_raw = symbol_data.get("ratios", {})

    # ---- Step 3: Analysis pipeline -----------------------------------
    current_price = price_raw.get("current_price")
    total_shares = price_raw.get("total_shares")

    valuation_data = compute_valuation(
        current_price=current_price,
        ratios=ratios_raw,
        financials=financials_raw,
        total_shares=total_shares,
    )

    technical_data = compute_technical(history_data)

    risk_data = assess_risk(
        price_data=price_raw,
        financials=financials_raw,
        technical=technical_data,
        price_history=history_data,
    )

    macro_data = get_macro_context(mbi10_data)

    verdict_data = generate_verdict(
        valuation=valuation_data,
        technical=technical_data,
        risk=risk_data,
        financials=financials_raw,
        ratios=ratios_raw,
    )

    # ---- Step 4: Assemble response -----------------------------------
    report = ResearchReport(
        ticker=ticker,
        company=CompanyProfile(**company_raw),
        price=PriceData(**price_raw),
        price_history=[PricePoint(**p) for p in history_data],
        financials=[FinancialData(**f) for f in financials_raw],
        ratios=FinancialRatios(**ratios_raw),
        valuation=ValuationMetrics(**valuation_data),
        technical=TechnicalAnalysis(**technical_data),
        macro=MacroContext(**macro_data),
        risk=RiskAssessment(**risk_data),
        verdict=Verdict(**verdict_data),
        generated_at=_now_iso(),
    )

    return report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
