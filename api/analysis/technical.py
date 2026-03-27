"""Technical analysis: trend, support/resistance, momentum, volume."""

from __future__ import annotations

import statistics
from typing import Any


def compute_technical(
    price_history: list[dict[str, Any]],
    mbi10_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run technical analysis on historical price data.

    *price_history* should be sorted oldest-first with keys matching
    the ``PricePoint`` schema.

    Returns a dict matching the ``TechnicalAnalysis`` schema.
    """
    result: dict[str, Any] = {
        "trend": None,
        "sma_short": None,
        "sma_long": None,
        "support": None,
        "resistance": None,
        "momentum": None,
        "momentum_pct": None,
        "volume_trend": None,
        "avg_volume_10d": None,
        "avg_volume_30d": None,
        "week52_position": None,
        "ytd_return_pct": None,
        "days_since_last_trade": None,
        "beta_vs_mbi10": None,
        "score": 50.0,
    }

    # Extract closing prices (last_trade_price) and volumes, ignoring None.
    prices = [
        p["last_trade_price"]
        for p in price_history
        if p.get("last_trade_price") is not None
    ]
    volumes = [
        p["volume"]
        for p in price_history
        if p.get("volume") is not None and p["volume"] > 0
    ]

    if len(prices) < 5:
        return result

    # ---- Trend (SMA crossover) ----------------------------------------
    short_window = min(50, len(prices) // 2) or 1
    long_window = min(200, len(prices)) or short_window

    sma_short = _sma(prices, short_window)
    sma_long = _sma(prices, long_window)

    result["sma_short"] = round(sma_short, 2) if sma_short else None
    result["sma_long"] = round(sma_long, 2) if sma_long else None

    if sma_short is not None and sma_long is not None:
        if sma_short > sma_long * 1.01:
            result["trend"] = "Bullish"
        elif sma_short < sma_long * 0.99:
            result["trend"] = "Bearish"
        else:
            result["trend"] = "Neutral"

    # ---- Support / Resistance (last 30 trading days) ------------------
    recent_30 = prices[-30:] if len(prices) >= 30 else prices
    highs = [
        p["max_price"]
        for p in price_history[-30:]
        if p.get("max_price") is not None
    ] or recent_30
    lows = [
        p["min_price"]
        for p in price_history[-30:]
        if p.get("min_price") is not None
    ] or recent_30

    result["support"] = round(min(lows), 2) if lows else None
    result["resistance"] = round(max(highs), 2) if highs else None

    # ---- Momentum (% up days in last 14 trading days) -----------------
    recent_14 = prices[-14:] if len(prices) >= 14 else prices
    if len(recent_14) >= 2:
        up_days = sum(
            1 for i in range(1, len(recent_14)) if recent_14[i] > recent_14[i - 1]
        )
        total_days = len(recent_14) - 1
        momentum_pct = round(up_days / total_days * 100, 1) if total_days else 0

        result["momentum_pct"] = momentum_pct
        if momentum_pct > 64:
            result["momentum"] = "Strong"
        elif momentum_pct >= 43:
            result["momentum"] = "Moderate"
        else:
            result["momentum"] = "Weak"

    # ---- Volume trend -------------------------------------------------
    if len(volumes) >= 10:
        avg_10 = statistics.mean(volumes[-10:])
        avg_30 = statistics.mean(volumes[-30:]) if len(volumes) >= 30 else statistics.mean(volumes)

        result["avg_volume_10d"] = round(avg_10, 0)
        result["avg_volume_30d"] = round(avg_30, 0)

        if avg_30 > 0:
            ratio = avg_10 / avg_30
            if ratio > 1.2:
                result["volume_trend"] = "Increasing"
            elif ratio < 0.8:
                result["volume_trend"] = "Decreasing"
            else:
                result["volume_trend"] = "Stable"

    # ---- 52-week position ---------------------------------------------
    if len(prices) >= 20:
        high_52 = max(prices)
        low_52 = min(prices)
        current = prices[-1]
        span = high_52 - low_52
        if span > 0:
            result["week52_position"] = round((current - low_52) / span, 3)

    # ---- YTD return ----------------------------------------------------
    result["ytd_return_pct"] = _compute_ytd_return(price_history)

    # ---- Days since last trade ----------------------------------------
    result["days_since_last_trade"] = _compute_days_since_last_trade(price_history)

    # ---- Beta vs MBI10 ------------------------------------------------
    if mbi10_history:
        result["beta_vs_mbi10"] = _compute_beta(price_history, mbi10_history)

    # ---- Technical score (0-100) --------------------------------------
    result["score"] = _compute_score(result)

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sma(prices: list[float], window: int) -> float | None:
    """Simple moving average of the last *window* prices."""
    if not prices or window <= 0:
        return None
    segment = prices[-window:]
    return sum(segment) / len(segment)


def _compute_ytd_return(price_history: list[dict[str, Any]]) -> float | None:
    """Compute year-to-date return percentage."""
    if not price_history:
        return None

    from datetime import date as _date

    current_year = _date.today().year
    # Find the first trading day of the current year.
    ytd_start_price = None
    for p in price_history:
        d = p.get("date", "")
        if d.startswith(str(current_year)):
            price = p.get("last_trade_price")
            if price is not None:
                ytd_start_price = price
                break

    if ytd_start_price is None or ytd_start_price == 0:
        return None

    # Latest price.
    latest_price = None
    for p in reversed(price_history):
        if p.get("last_trade_price") is not None:
            latest_price = p["last_trade_price"]
            break

    if latest_price is None:
        return None

    return round((latest_price - ytd_start_price) / ytd_start_price * 100, 2)


def _compute_days_since_last_trade(price_history: list[dict[str, Any]]) -> int | None:
    """Compute the number of calendar days since the most recent trade."""
    if not price_history:
        return None

    from datetime import date as _date, datetime as _datetime

    # Walk backwards to find the latest entry with volume > 0.
    for p in reversed(price_history):
        vol = p.get("volume")
        if vol is not None and vol > 0:
            date_str = p.get("date", "")
            try:
                # Try common formats.
                for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d.%m.%Y"):
                    try:
                        trade_date = _datetime.strptime(date_str, fmt).date()
                        return (_date.today() - trade_date).days
                    except ValueError:
                        continue
            except Exception:
                pass
            return None
    return None


def _compute_beta(
    price_history: list[dict[str, Any]],
    mbi10_history: list[dict[str, Any]],
) -> float | None:
    """Compute beta of the stock vs. MBI10 index using daily returns."""
    # Build date-indexed return maps.
    def _returns_by_date(data: list[dict[str, Any]], price_key: str) -> dict[str, float]:
        prices = [(p["date"], p[price_key]) for p in data if p.get(price_key) is not None]
        result: dict[str, float] = {}
        for i in range(1, len(prices)):
            if prices[i - 1][1] and prices[i - 1][1] > 0:
                ret = (prices[i][1] - prices[i - 1][1]) / prices[i - 1][1]
                result[prices[i][0]] = ret
        return result

    stock_returns = _returns_by_date(price_history, "last_trade_price")
    index_returns = _returns_by_date(mbi10_history, "value")

    # Align by date.
    common_dates = sorted(set(stock_returns) & set(index_returns))
    if len(common_dates) < 20:
        return None

    sr = [stock_returns[d] for d in common_dates]
    ir = [index_returns[d] for d in common_dates]

    mean_s = sum(sr) / len(sr)
    mean_i = sum(ir) / len(ir)

    cov = sum((s - mean_s) * (i - mean_i) for s, i in zip(sr, ir)) / len(sr)
    var_i = sum((i - mean_i) ** 2 for i in ir) / len(ir)

    if var_i == 0:
        return None

    return round(cov / var_i, 2)


def _compute_score(tech: dict[str, Any]) -> float:
    """Produce a 0-100 technical score."""
    score = 50.0  # neutral baseline

    # Trend component.
    trend = tech.get("trend")
    if trend == "Bullish":
        score += 15
    elif trend == "Bearish":
        score -= 15

    # Momentum component.
    momentum = tech.get("momentum")
    if momentum == "Strong":
        score += 15
    elif momentum == "Moderate":
        score += 5
    elif momentum == "Weak":
        score -= 10

    # Volume component.
    vol = tech.get("volume_trend")
    if vol == "Increasing":
        score += 5
    elif vol == "Decreasing":
        score -= 5

    # 52-week position (mid-range is neutral, near high is good, near low is bad).
    pos = tech.get("week52_position")
    if pos is not None:
        score += (pos - 0.5) * 20  # +/- 10

    return max(0, min(100, round(score, 1)))
