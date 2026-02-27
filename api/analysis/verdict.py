"""Rating engine: combine analysis outputs into a final investment verdict."""

from __future__ import annotations

from typing import Any


def generate_verdict(
    valuation: dict[str, Any],
    technical: dict[str, Any],
    risk: dict[str, Any],
    financials: list[dict[str, Any]],
    ratios: dict[str, Any],
) -> dict[str, Any]:
    """Produce a final investment verdict with score, rating, and narrative.

    Scoring breakdown (0-100):
        - Valuation score  : 30 %
        - Growth score     : 25 %
        - Technical score  : 20 %
        - Risk penalty     : 25 %  (higher risk_score = lower penalty)

    Returns a dict matching the ``Verdict`` schema.
    """
    val_score = valuation.get("score", 50)
    tech_score = technical.get("score", 50)
    growth_score = _growth_score(financials, ratios)
    risk_score = risk.get("score", 50)  # 0-100, higher = safer

    total = (
        val_score * 0.30
        + growth_score * 0.25
        + tech_score * 0.20
        + risk_score * 0.25
    )
    total = round(total, 1)

    # Rating buckets.
    if total >= 80:
        rating = "Strong Buy"
    elif total >= 65:
        rating = "Buy"
    elif total >= 40:
        rating = "Hold"
    else:
        rating = "Avoid"

    # Narrative.
    positives = _key_positives(valuation, technical, risk, financials, ratios)
    negatives = _key_negatives(valuation, technical, risk, financials, ratios)
    summary = _build_summary(rating, total, valuation, technical, risk)

    return {
        "rating": rating,
        "total_score": total,
        "valuation_score": round(val_score, 1),
        "growth_score": round(growth_score, 1),
        "technical_score": round(tech_score, 1),
        "risk_score": round(risk_score, 1),
        "summary": summary,
        "key_positives": positives,
        "key_negatives": negatives,
    }


# ---------------------------------------------------------------------------
# Growth score
# ---------------------------------------------------------------------------

def _growth_score(financials: list[dict[str, Any]], ratios: dict[str, Any]) -> float:
    """Score 0-100 based on revenue and profit growth trends."""
    if not financials:
        return 50.0  # neutral when data is missing

    sorted_fin = sorted(financials, key=lambda f: f.get("year", 0))
    score = 50.0

    # Revenue trend.
    revenues = [f.get("revenue") for f in sorted_fin if f.get("revenue") is not None]
    if len(revenues) >= 2:
        if revenues[-1] > revenues[0]:
            score += 15
        elif revenues[-1] < revenues[0]:
            score -= 10

    # Net profit trend.
    profits = [f.get("net_profit") for f in sorted_fin if f.get("net_profit") is not None]
    if len(profits) >= 2:
        if profits[-1] > profits[0]:
            score += 15
        elif profits[-1] < profits[0]:
            score -= 10

    # ROE bonus.
    roe = ratios.get("roe")
    if roe is not None:
        if roe > 15:
            score += 10
        elif roe > 8:
            score += 5
        elif roe < 0:
            score -= 10

    return max(0, min(100, score))


# ---------------------------------------------------------------------------
# Narrative helpers
# ---------------------------------------------------------------------------

def _key_positives(
    valuation: dict, technical: dict, risk: dict,
    financials: list[dict], ratios: dict,
) -> list[str]:
    positives: list[str] = []

    if valuation.get("pe_assessment") == "Undervalued":
        positives.append("Attractive valuation with low P/E ratio")
    if valuation.get("pb_assessment") == "Undervalued":
        positives.append("Trading below book value")
    if valuation.get("dividend_assessment") in ("High yield", "Moderate yield"):
        positives.append(
            f"Dividend yield of {valuation.get('dividend_yield', 0):.1f}%"
        )
    if technical.get("trend") == "Bullish":
        positives.append("Bullish price trend (short MA above long MA)")
    if technical.get("momentum") == "Strong":
        positives.append("Strong upward momentum")
    if risk.get("liquidity_risk") == "Low":
        positives.append("Good trading liquidity")

    roe = ratios.get("roe")
    if roe is not None and roe > 12:
        positives.append(f"Strong return on equity ({roe:.1f}%)")

    return positives[:4]


def _key_negatives(
    valuation: dict, technical: dict, risk: dict,
    financials: list[dict], ratios: dict,
) -> list[str]:
    negatives: list[str] = []

    if valuation.get("pe_assessment") == "Overvalued":
        negatives.append("Elevated P/E ratio suggests overvaluation")
    if valuation.get("pb_assessment") == "Overvalued":
        negatives.append("Trading at a premium to book value")
    if valuation.get("pe_assessment") == "Negative earnings":
        negatives.append("Company is currently unprofitable")
    if technical.get("trend") == "Bearish":
        negatives.append("Bearish price trend")
    if technical.get("momentum") == "Weak":
        negatives.append("Weak price momentum")
    if risk.get("liquidity_risk") in ("Very High", "High"):
        negatives.append(
            f"{risk['liquidity_risk']} liquidity risk -- difficult to exit position"
        )
    if risk.get("volatility_risk") == "High":
        negatives.append("High price volatility")
    if risk.get("financial_risk") == "High":
        negatives.append("High financial leverage")

    return negatives[:4]


def _build_summary(
    rating: str,
    score: float,
    valuation: dict,
    technical: dict,
    risk: dict,
) -> str:
    """Generate a 2-3 sentence narrative summary."""
    parts: list[str] = []

    parts.append(
        f"Overall rating is {rating} with a composite score of {score:.0f}/100."
    )

    val_text = valuation.get("overall_assessment", "unknown")
    parts.append(f"Valuation appears {val_text.lower()}.")

    trend = technical.get("trend", "neutral")
    risk_level = risk.get("overall_risk", "medium")
    parts.append(
        f"Technical trend is {trend.lower()} with {risk_level.lower()} overall risk."
    )

    return " ".join(parts)
