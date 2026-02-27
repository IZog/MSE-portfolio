"""Pydantic models for the MSE Research Dashboard API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CompanyProfile(BaseModel):
    """Basic company information scraped from the MSE symbol page."""

    ticker: str
    name: str | None = None
    description: str | None = None
    address: str | None = None
    sector: str | None = None


class PriceData(BaseModel):
    """Current price snapshot and 52-week range."""

    current_price: float | None = None
    price_change_pct: float | None = None
    high_52w: float | None = None
    low_52w: float | None = None
    total_shares: int | None = None
    market_cap: float | None = None


class PricePoint(BaseModel):
    """Single row from the symbol-history table."""

    date: str
    last_trade_price: float | None = None
    max_price: float | None = None
    min_price: float | None = None
    avg_price: float | None = None
    pct_change: float | None = None
    volume: int | None = None
    turnover_best: float | None = None
    total_turnover: float | None = None


class FinancialData(BaseModel):
    """Multi-year income-statement / balance-sheet items."""

    year: int
    revenue: float | None = None
    operating_profit: float | None = None
    net_profit: float | None = None
    equity: float | None = None
    total_assets: float | None = None
    total_liabilities: float | None = None


class FinancialRatios(BaseModel):
    """Key ratios scraped directly from the symbol page."""

    pe_ratio: float | None = Field(None, description="Price / Earnings")
    eps: float | None = Field(None, description="Earnings per share (MKD)")
    roa: float | None = Field(None, description="Return on assets (%)")
    roe: float | None = Field(None, description="Return on equity (%)")
    book_value_per_share: float | None = None
    dividend_per_share: float | None = None
    dividend_yield: float | None = Field(None, description="Dividend yield (%)")
    market_cap: float | None = Field(None, description="Market capitalisation (MKD)")


class ValuationMetrics(BaseModel):
    """Output of the valuation analysis module."""

    pe_ratio: float | None = None
    pe_assessment: str | None = None  # Undervalued / Fair / Overvalued
    pb_ratio: float | None = None
    pb_assessment: str | None = None
    dividend_yield: float | None = None
    dividend_assessment: str | None = None
    earnings_yield: float | None = None
    overall_assessment: str | None = None
    score: float = Field(0, description="0-100 valuation score")


class TechnicalAnalysis(BaseModel):
    """Output of the technical analysis module."""

    trend: str | None = None  # Bullish / Bearish / Neutral
    sma_short: float | None = None
    sma_long: float | None = None
    support: float | None = None
    resistance: float | None = None
    momentum: str | None = None  # Strong / Moderate / Weak
    momentum_pct: float | None = None
    volume_trend: str | None = None  # Increasing / Decreasing / Stable
    avg_volume_10d: float | None = None
    avg_volume_30d: float | None = None
    week52_position: float | None = None
    score: float = Field(0, description="0-100 technical score")


class MacroContext(BaseModel):
    """MBI10 index data plus static macroeconomic indicators."""

    mbi10_value: float | None = None
    mbi10_change_pct: float | None = None
    gdp_growth: float | None = None
    inflation: float | None = None
    policy_rate: float | None = None
    last_updated: str | None = None


class RiskAssessment(BaseModel):
    """Multi-factor risk scoring output."""

    liquidity_risk: str | None = None  # Very High / High / Medium / Low
    volatility_risk: str | None = None
    financial_risk: str | None = None
    market_risk: str = "Medium"
    overall_risk: str | None = None
    factors: list[str] = Field(default_factory=list)
    score: float = Field(0, description="0-100 risk score (higher = safer)")


class Verdict(BaseModel):
    """Final investment verdict produced by the rating engine."""

    rating: str  # Strong Buy / Buy / Hold / Avoid
    total_score: float
    valuation_score: float
    growth_score: float
    technical_score: float
    risk_score: float
    summary: str
    key_positives: list[str] = Field(default_factory=list)
    key_negatives: list[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    """Complete research report returned by GET /api/research/{ticker}."""

    ticker: str
    company: CompanyProfile
    price: PriceData
    price_history: list[PricePoint] = Field(default_factory=list)
    financials: list[FinancialData] = Field(default_factory=list)
    ratios: FinancialRatios
    valuation: ValuationMetrics
    technical: TechnicalAnalysis
    macro: MacroContext
    risk: RiskAssessment
    verdict: Verdict
    generated_at: str


class TickerInfo(BaseModel):
    """Single entry from the trading-schedule page."""

    symbol: str
    name: str | None = None
    isin: str | None = None
    market_segment: str | None = None
