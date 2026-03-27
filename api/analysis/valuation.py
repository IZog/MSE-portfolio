"""Valuation analysis: P/E, P/B, dividend yield assessment."""

from __future__ import annotations

from typing import Any


def compute_valuation(
    current_price: float | None,
    ratios: dict[str, Any],
    financials: list[dict[str, Any]],
    total_shares: int | None,
) -> dict[str, Any]:
    """Assess valuation using scraped ratios and financial data.

    Returns a dict matching the ``ValuationMetrics`` schema.
    """
    pe = ratios.get("pe_ratio")
    eps = ratios.get("eps")
    book_value_ps = ratios.get("book_value_per_share")
    div_yield = ratios.get("dividend_yield")
    market_cap = ratios.get("market_cap")

    # Compute P/B if we have the pieces.
    pb: float | None = None
    if current_price and book_value_ps and book_value_ps > 0:
        pb = round(current_price / book_value_ps, 2)

    # Earnings yield.
    earnings_yield: float | None = None
    if current_price and eps and current_price > 0:
        earnings_yield = round(eps / current_price * 100, 2)

    # ---------- Assessments ----------

    pe_assessment = _assess_pe(pe)
    pb_assessment = _assess_pb(pb)
    div_assessment = _assess_dividend(div_yield)

    # Overall: weighted vote.
    assessments = [a for a in (pe_assessment, pb_assessment, div_assessment) if a]
    overall = _overall_assessment(assessments)

    # Score (0-100).
    score = _compute_score(pe, pb, div_yield)

    # ---------- V2: EV/EBITDA, deposit spread, net margin --------

    ev_ebitda: float | None = None
    ev_ebitda_note: str | None = None
    deposit_rate_spread: float | None = None
    net_profit_margin: float | None = None

    # EV/EBITDA — estimate EBITDA as operating_profit × 1.15 (rough DA proxy).
    if financials:
        latest = max(financials, key=lambda f: f.get("year", 0))
        op_profit = latest.get("operating_profit")
        total_liab = latest.get("total_liabilities", 0) or 0

        # Determine market cap: prefer scraped value, else compute from price × shares.
        mkt_cap = market_cap
        if not mkt_cap and current_price and total_shares and total_shares > 0:
            mkt_cap = current_price * total_shares

        if op_profit and op_profit > 0 and mkt_cap and mkt_cap > 0:
            ebitda_est = op_profit * 1.15
            ev = mkt_cap + total_liab  # simplified: EV = market cap + debt
            ev_ebitda = round(ev / ebitda_est, 2)
            ev_ebitda_note = "EBITDA estimated as Operating Profit × 1.15"
        elif op_profit is not None and op_profit <= 0:
            ev_ebitda_note = "N/A — negative operating profit"

        # Net profit margin.
        revenue = latest.get("revenue")
        net_p = latest.get("net_profit")
        if revenue and revenue > 0 and net_p is not None:
            net_profit_margin = round(net_p / revenue * 100, 2)

    # Deposit rate spread: earnings yield minus deposit rate.
    deposit_rate = 3.0  # Estimated avg deposit rate (Mar 2026)
    if earnings_yield is not None:
        deposit_rate_spread = round(earnings_yield - deposit_rate, 2)

    return {
        "pe_ratio": pe,
        "pe_assessment": pe_assessment,
        "pb_ratio": pb,
        "pb_assessment": pb_assessment,
        "dividend_yield": div_yield,
        "dividend_assessment": div_assessment,
        "earnings_yield": earnings_yield,
        "overall_assessment": overall,
        "ev_ebitda": ev_ebitda,
        "ev_ebitda_note": ev_ebitda_note,
        "deposit_rate_spread": deposit_rate_spread,
        "net_profit_margin": net_profit_margin,
        "score": score,
    }


# ---------------------------------------------------------------------------
# Assessment helpers
# ---------------------------------------------------------------------------

def _assess_pe(pe: float | None) -> str | None:
    if pe is None:
        return None
    if pe < 0:
        return "Negative earnings"
    if pe < 10:
        return "Undervalued"
    if pe <= 20:
        return "Fair"
    return "Overvalued"


def _assess_pb(pb: float | None) -> str | None:
    if pb is None:
        return None
    if pb < 0:
        return "Negative book value"
    if pb < 1:
        return "Undervalued"
    if pb <= 3:
        return "Fair"
    return "Overvalued"


def _assess_dividend(div_yield: float | None) -> str | None:
    if div_yield is None:
        return None
    if div_yield <= 0:
        return "No dividend"
    if div_yield >= 5:
        return "High yield"
    if div_yield >= 2:
        return "Moderate yield"
    return "Low yield"


def _overall_assessment(assessments: list[str]) -> str:
    if not assessments:
        return "Insufficient data"

    score_map = {
        "Undervalued": 2,
        "High yield": 2,
        "Fair": 1,
        "Moderate yield": 1,
        "Low yield": 0,
        "Overvalued": -1,
        "Negative earnings": -1,
        "Negative book value": -1,
        "No dividend": 0,
    }
    total = sum(score_map.get(a, 0) for a in assessments)
    avg = total / len(assessments)

    if avg >= 1.5:
        return "Undervalued"
    if avg >= 0.5:
        return "Fair"
    if avg >= -0.5:
        return "Fairly valued"
    return "Overvalued"


def _compute_score(
    pe: float | None,
    pb: float | None,
    div_yield: float | None,
) -> float:
    """Produce a 0-100 valuation score (higher = more attractively valued)."""
    components: list[float] = []

    if pe is not None and pe > 0:
        # Lower P/E is better. P/E of 5 -> 100, P/E of 30 -> 0.
        components.append(max(0, min(100, (30 - pe) / 25 * 100)))
    if pb is not None and pb > 0:
        # P/B of 0.5 -> 100, P/B of 4 -> 0.
        components.append(max(0, min(100, (4 - pb) / 3.5 * 100)))
    if div_yield is not None:
        # Div yield of 8%+ -> 100, 0% -> 20.
        components.append(max(0, min(100, 20 + div_yield * 10)))

    if not components:
        return 50.0  # neutral default
    return round(sum(components) / len(components), 1)
