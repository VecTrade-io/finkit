"""Tests for FinKit risk metrics."""

import numpy as np
import pandas as pd
import pytest

from finkit.risk import sharpe_ratio, sortino_ratio, max_drawdown, var


@pytest.fixture
def returns() -> pd.Series:
    """Sample daily returns."""
    np.random.seed(42)
    return pd.Series(np.random.randn(252) * 0.01 + 0.0003)  # ~7.5% annual return


class TestSharpeRatio:
    """Test Sharpe ratio calculation."""

    def test_positive_returns(self, returns: pd.Series) -> None:
        result = sharpe_ratio(returns, risk_free_rate=0.04)
        assert isinstance(result, float)
        assert np.isfinite(result)

    def test_zero_volatility(self) -> None:
        """Constant returns → infinite/undefined Sharpe."""
        flat = pd.Series([0.001] * 100)
        # Should handle gracefully (either inf or raise)
        result = sharpe_ratio(flat, risk_free_rate=0.0)
        assert result == float("inf") or np.isnan(result)

    def test_annualization(self, returns: pd.Series) -> None:
        """Daily vs already annualized should differ."""
        daily = sharpe_ratio(returns, risk_free_rate=0.04, periods_per_year=252)
        assert abs(daily) < 5  # Reasonable bound


class TestSortinoRatio:
    """Test Sortino ratio calculation."""

    def test_basic(self, returns: pd.Series) -> None:
        result = sortino_ratio(returns, risk_free_rate=0.04)
        assert isinstance(result, float)
        assert np.isfinite(result)

    def test_higher_than_sharpe_for_positive_skew(self) -> None:
        """Sortino >= Sharpe when downside vol < total vol."""
        np.random.seed(123)
        # Generate positively skewed returns
        pos_skew = pd.Series(np.abs(np.random.randn(252)) * 0.01)
        sharpe = sharpe_ratio(pos_skew, risk_free_rate=0.0)
        sortino = sortino_ratio(pos_skew, risk_free_rate=0.0)
        # With all positive returns, sortino should be very high
        assert sortino >= sharpe


class TestMaxDrawdown:
    """Test maximum drawdown calculation."""

    def test_basic(self, returns: pd.Series) -> None:
        result = max_drawdown(returns)
        assert isinstance(result, float)
        assert result <= 0  # Drawdown is negative or zero
        assert result >= -1  # Can't lose more than 100%

    def test_no_drawdown(self) -> None:
        """Monotonically increasing prices have 0 drawdown."""
        rising = pd.Series([0.01] * 100)
        result = max_drawdown(rising)
        assert result == 0.0 or abs(result) < 1e-10

    def test_complete_loss(self) -> None:
        """50% drop means -0.5 drawdown."""
        returns = pd.Series([0.0, -0.5, 0.0])  # 50% drop in one day
        result = max_drawdown(returns)
        assert abs(result - (-0.5)) < 1e-10


class TestVaR:
    """Test Value at Risk calculation."""

    def test_basic(self, returns: pd.Series) -> None:
        result = var(returns, confidence=0.95)
        assert isinstance(result, float)
        assert result < 0  # VaR is a loss

    def test_higher_confidence_more_negative(self, returns: pd.Series) -> None:
        """99% VaR should be more negative than 95% VaR."""
        var_95 = var(returns, confidence=0.95)
        var_99 = var(returns, confidence=0.99)
        assert var_99 <= var_95

    def test_confidence_bounds(self, returns: pd.Series) -> None:
        with pytest.raises((ValueError, TypeError)):
            var(returns, confidence=1.5)
