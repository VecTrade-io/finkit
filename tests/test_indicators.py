"""Tests for FinKit technical indicators."""

import numpy as np
import pandas as pd
import pytest

from finkit.indicators import sma, ema, rsi, macd, bollinger_bands


@pytest.fixture
def prices() -> pd.Series:
    """Sample price data for testing."""
    np.random.seed(42)
    return pd.Series(100 + np.cumsum(np.random.randn(100) * 2))


class TestSMA:
    """Test Simple Moving Average."""

    def test_basic_calculation(self, prices: pd.Series) -> None:
        result = sma(prices, period=20)
        assert len(result) == len(prices)
        # First 19 values should be NaN
        assert result.iloc[:19].isna().all()
        # Value at index 19 should be mean of first 20 prices
        expected = prices.iloc[:20].mean()
        assert abs(result.iloc[19] - expected) < 1e-10

    def test_period_validation(self, prices: pd.Series) -> None:
        with pytest.raises((ValueError, TypeError)):
            sma(prices, period=0)

    def test_single_period(self, prices: pd.Series) -> None:
        result = sma(prices, period=1)
        pd.testing.assert_series_equal(result, prices, check_names=False)


class TestEMA:
    """Test Exponential Moving Average."""

    def test_basic_calculation(self, prices: pd.Series) -> None:
        result = ema(prices, period=20)
        assert len(result) == len(prices)
        # EMA should be close to price at the end for trending data
        assert not result.iloc[-1:].isna().any()

    def test_faster_than_sma_on_uptrend(self) -> None:
        """EMA reacts faster to price changes than SMA."""
        uptrend = pd.Series(range(1, 51), dtype=float)
        ema_result = ema(uptrend, period=10)
        sma_result = sma(uptrend, period=10)
        # In uptrend, EMA should be higher (closer to current price)
        assert ema_result.iloc[-1] > sma_result.iloc[-1]


class TestRSI:
    """Test Relative Strength Index."""

    def test_basic_calculation(self, prices: pd.Series) -> None:
        result = rsi(prices, period=14)
        assert len(result) == len(prices)
        # RSI should be between 0 and 100
        valid = result.dropna()
        assert (valid >= 0).all()
        assert (valid <= 100).all()

    def test_overbought_signal(self) -> None:
        """Strongly rising prices should give high RSI."""
        rising = pd.Series(range(1, 51), dtype=float)
        result = rsi(rising, period=14)
        assert result.iloc[-1] > 90

    def test_oversold_signal(self) -> None:
        """Strongly falling prices should give low RSI."""
        falling = pd.Series(range(50, 0, -1), dtype=float)
        result = rsi(falling, period=14)
        assert result.iloc[-1] < 10


class TestMACD:
    """Test MACD indicator."""

    def test_returns_three_series(self, prices: pd.Series) -> None:
        macd_line, signal, histogram = macd(prices)
        assert len(macd_line) == len(prices)
        assert len(signal) == len(prices)
        assert len(histogram) == len(prices)

    def test_histogram_is_difference(self, prices: pd.Series) -> None:
        macd_line, signal, histogram = macd(prices)
        valid_idx = ~(macd_line.isna() | signal.isna())
        diff = macd_line[valid_idx] - signal[valid_idx]
        pd.testing.assert_series_equal(histogram[valid_idx], diff, check_names=False)

    def test_custom_periods(self, prices: pd.Series) -> None:
        macd_line, signal, histogram = macd(prices, fast=8, slow=21, signal_period=5)
        assert not macd_line.iloc[-1:].isna().any()


class TestBollingerBands:
    """Test Bollinger Bands."""

    def test_returns_three_series(self, prices: pd.Series) -> None:
        upper, middle, lower = bollinger_bands(prices, period=20, std_dev=2.0)
        assert len(upper) == len(prices)
        assert len(middle) == len(prices)
        assert len(lower) == len(prices)

    def test_middle_is_sma(self, prices: pd.Series) -> None:
        _, middle, _ = bollinger_bands(prices, period=20)
        expected = sma(prices, period=20)
        pd.testing.assert_series_equal(middle, expected, check_names=False)

    def test_band_ordering(self, prices: pd.Series) -> None:
        """Upper > Middle > Lower always."""
        upper, middle, lower = bollinger_bands(prices, period=20)
        valid_idx = ~upper.isna()
        assert (upper[valid_idx] >= middle[valid_idx]).all()
        assert (middle[valid_idx] >= lower[valid_idx]).all()

    def test_wider_bands_with_higher_std(self, prices: pd.Series) -> None:
        upper1, _, lower1 = bollinger_bands(prices, period=20, std_dev=1.0)
        upper2, _, lower2 = bollinger_bands(prices, period=20, std_dev=2.0)
        valid_idx = ~upper1.isna()
        width1 = upper1[valid_idx] - lower1[valid_idx]
        width2 = upper2[valid_idx] - lower2[valid_idx]
        assert (width2 > width1).all()
