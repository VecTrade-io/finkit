"""Risk metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sharpe_ratio(
    returns: pd.Series, risk_free_rate: float = 0.0, periods: int = 252, periods_per_year: int | None = None
) -> float:
    """Annualized Sharpe Ratio.

    Args:
        returns: Series of period returns.
        risk_free_rate: Annual risk-free rate.
        periods: Periods per year (e.g., 252 for daily).
        periods_per_year: Alias for periods.
    """
    ann = periods_per_year if periods_per_year is not None else periods
    excess = returns - risk_free_rate / ann
    std = excess.std()
    if std < 1e-12 or np.isnan(std):
        return float("inf") if excess.mean() >= 0 else float("-inf")
    return float(np.sqrt(ann) * excess.mean() / std)


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods: int = 252) -> float:
    """Annualized Sortino Ratio (downside deviation only)."""
    excess = returns - risk_free_rate / periods
    downside = excess[excess < 0]
    downside_std = np.sqrt((downside**2).mean())
    return float(np.sqrt(periods) * excess.mean() / downside_std) if downside_std > 0 else float("inf")


def max_drawdown(returns: pd.Series) -> float:
    """Maximum drawdown from peak.

    Args:
        returns: Series of period returns (not cumulative).

    Returns:
        Maximum drawdown as a negative float (e.g., -0.15 for 15% drawdown).
    """
    equity = (1 + returns).cumprod()
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    return float(drawdown.min())


def var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Value at Risk (historical method)."""
    return float(np.percentile(returns.dropna(), (1 - confidence) * 100))
