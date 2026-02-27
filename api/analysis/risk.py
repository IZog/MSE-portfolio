"""Multi-factor risk scoring for MSE stocks."""

from __future__ import annotations

import statistics
from typing import Any


def assess_risk(
    price_data: dict[str, Any],
    financials: list[dict[str, Any]],
    technical: dict[str, Any],
    price_history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute a multi-factor risk assessment.

    Returns a dict matching the ``RiskAssessment`` schema.
    """
    factors: list[str] = []

    # ---- Liquidity risk -----------------------------------------------
    volumes = [
        p["volume"]
        for p in price_history
        if p.get("volume") is not None
    ]
    avg_daily_volume = statistics.mean(volumes) if volumes else 0

    if avg_daily_volume < 100:
        liquidity_risk = "Very High"
        factors.append(
            f"Very low liquidity: avg daily volume {avg_daily_volume:.0f} shares"
        )
    elif avg_daily_volume < 500:
        liquidity_risk = "High"
        factors.append(
            f"Low liquidity: avg daily volume {avg_daily_volume:.0f} shares"
        )
    elif avg_daily_volume < 2000:
        liquidity_risk = "Medium"
        factors.append(
            f"Moderate liquidity: avg daily volume {avg_daily_volume:.0f} shares"
        )
    else:
        liquidity_risk = "Low"

    # ---- Volatility risk (std dev of daily returns) -------------------
    prices = [
        p["last_trade_price"]
        for p in price_history
        if p.get("last_trade_price") is not None
    ]
    daily_returns: list[float] = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0:
            daily_returns.append((prices[i] - prices[i - 1]) / prices[i - 1] * 100)

    if len(daily_returns) >= 5:
        vol_std = statistics.stdev(daily_returns)
        if vol_std > 3:
            volatility_risk = "High"
            factors.append(f"High price volatility: {vol_std:.1f}% daily std dev")
        elif vol_std > 1.5:
            volatility_risk = "Medium"
            factors.append(f"Moderate price volatility: {vol_std:.1f}% daily std dev")
        else:
            volatility_risk = "Low"
    else:
        volatility_risk = "Medium"
        factors.append("Insufficient price history to assess volatility accurately")

    # ---- Financial risk (debt / equity) -------------------------------
    financial_risk = "Medium"
    if financials:
        latest = max(financials, key=lambda f: f.get("year", 0))
        equity = latest.get("equity")
        liabilities = latest.get("total_liabilities")
        if equity and liabilities and equity > 0:
            de_ratio = liabilities / equity
            if de_ratio > 1.0:
                financial_risk = "High"
                factors.append(
                    f"High leverage: debt/equity ratio {de_ratio:.2f}"
                )
            elif de_ratio > 0.5:
                financial_risk = "Medium"
                factors.append(
                    f"Moderate leverage: debt/equity ratio {de_ratio:.2f}"
                )
            else:
                financial_risk = "Low"
        else:
            factors.append("Could not determine debt/equity ratio")

    # ---- Market risk (static for all MSE stocks) ----------------------
    market_risk = "Medium"
    factors.append(
        "Emerging/frontier market risk: MSE is a small, less-liquid exchange"
    )

    # ---- Overall: worst of individual risks ---------------------------
    risk_levels = ["Low", "Medium", "High", "Very High"]
    individual = [liquidity_risk, volatility_risk, financial_risk, market_risk]
    overall_risk = max(individual, key=lambda r: risk_levels.index(r))

    # Score: 0-100 where higher = safer.
    score = _risk_score(liquidity_risk, volatility_risk, financial_risk, market_risk)

    # ---- V2: Additional flags ------------------------------------------
    # Days since last trade flag.
    days_since_last_trade_flag = None
    from datetime import date as _date, datetime as _datetime

    for p in reversed(price_history):
        vol = p.get("volume")
        if vol is not None and vol > 0:
            date_str = p.get("date", "")
            for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d.%m.%Y"):
                try:
                    trade_date = _datetime.strptime(date_str, fmt).date()
                    days_gap = (_date.today() - trade_date).days
                    if days_gap > 30:
                        days_since_last_trade_flag = f"Stale — no trade in {days_gap} days"
                        factors.append(f"No trading activity for {days_gap} days")
                    elif days_gap > 7:
                        days_since_last_trade_flag = f"Caution — last trade {days_gap} days ago"
                    else:
                        days_since_last_trade_flag = "Active"
                    break
                except ValueError:
                    continue
            break

    # Free float and ownership — not available from MSE scraping.
    free_float_flag = "Unknown — not disclosed on MSE"
    ownership_concentration_flag = "Unknown — not disclosed on MSE"

    return {
        "liquidity_risk": liquidity_risk,
        "volatility_risk": volatility_risk,
        "financial_risk": financial_risk,
        "market_risk": market_risk,
        "overall_risk": overall_risk,
        "days_since_last_trade_flag": days_since_last_trade_flag,
        "free_float_flag": free_float_flag,
        "ownership_concentration_flag": ownership_concentration_flag,
        "factors": factors,
        "score": score,
    }


def _risk_score(
    liquidity: str,
    volatility: str,
    financial: str,
    market: str,
) -> float:
    """Convert individual risk labels into a 0-100 safety score."""
    level_map = {"Low": 100, "Medium": 65, "High": 35, "Very High": 10}
    scores = [
        level_map.get(liquidity, 50),
        level_map.get(volatility, 50),
        level_map.get(financial, 50),
        level_map.get(market, 50),
    ]
    return round(sum(scores) / len(scores), 1)
