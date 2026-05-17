"""Edge-case tests for FinKit indicators and signals."""

import numpy as np
import pandas as pd
import pytest

from finkit.indicators import sma, ema, rsi, macd, bollinger_bands, atr, vwap, obv
from finkit.signals import crossover, crossunder


# ── Indicators: edge cases ──────────────────────────────────────────────


class TestEmptySeries:
    """Indicators should handle empty input without crashing."""

    def test_sma_empty(self) -> None:
        result = sma(pd.Series([], dtype=float), period=5)
        assert len(result) == 0

    def test_ema_empty(self) -> None:
        result = ema(pd.Series([], dtype=float), period=5)
        assert len(result) == 0

    def test_rsi_empty(self) -> None:
        result = rsi(pd.Series([], dtype=float), period=14)
        assert len(result) == 0

    def test_macd_empty(self) -> None:
        line, signal, hist = macd(pd.Series([], dtype=float))
        assert len(line) == 0
        assert len(signal) == 0
        assert len(hist) == 0

    def test_bollinger_empty(self) -> None:
        upper, mid, lower = bollinger_bands(pd.Series([], dtype=float))
        assert len(upper) == 0


class TestSingleValue:
    """Indicators should handle a single data point gracefully."""

    def test_sma_single(self) -> None:
        result = sma(pd.Series([100.0]), period=1)
        assert result.iloc[0] == pytest.approx(100.0)

    def test_ema_single(self) -> None:
        result = ema(pd.Series([100.0]), period=1)
        assert result.iloc[0] == pytest.approx(100.0)

    def test_rsi_single(self) -> None:
        result = rsi(pd.Series([100.0]), period=14)
        # Not enough data → NaN
        assert result.isna().all()

    def test_macd_single(self) -> None:
        line, signal, hist = macd(pd.Series([100.0]))
        assert len(line) == 1


class TestNaNHandling:
    """Indicators should propagate NaN without raising."""

    def test_sma_with_nan(self) -> None:
        data = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        result = sma(data, period=2)
        # Window containing NaN should produce NaN
        assert np.isnan(result.iloc[2])

    def test_ema_with_nan(self) -> None:
        data = pd.Series([1.0, np.nan, 3.0, 4.0, 5.0])
        result = ema(data, period=2)
        # EMA should still produce values (NaN propagates through ewm)
        assert len(result) == 5

    def test_rsi_with_nan(self) -> None:
        data = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
                          11.0, 12.0, 13.0, 14.0, 15.0, 16.0])
        result = rsi(data, period=14)
        assert len(result) == len(data)

    def test_all_nan(self) -> None:
        data = pd.Series([np.nan, np.nan, np.nan, np.nan])
        result = sma(data, period=2)
        assert result.isna().all()


class TestConstantSeries:
    """Indicators on constant data should produce known values."""

    def test_sma_constant(self) -> None:
        data = pd.Series([50.0] * 30)
        result = sma(data, period=10)
        valid = result.dropna()
        assert len(valid) > 0
        assert valid.sub(50.0).abs().max() < 1e-10

    def test_ema_constant(self) -> None:
        data = pd.Series([50.0] * 30)
        result = ema(data, period=10)
        assert result.iloc[-1] == pytest.approx(50.0)

    def test_rsi_constant(self) -> None:
        """Constant series → no gains or losses → RSI is NaN (0/0 division)."""
        data = pd.Series([100.0] * 30)
        result = rsi(data, period=14)
        valid = result.iloc[15:]
        # gain=0, loss=0 → rs=NaN → RSI is NaN
        assert valid.isna().all()

    def test_bollinger_constant_zero_width(self) -> None:
        """Constant series → std=0 → upper == middle == lower."""
        data = pd.Series([100.0] * 30)
        upper, middle, lower = bollinger_bands(data, period=10)
        valid = ~upper.isna()
        pd.testing.assert_series_equal(upper[valid], middle[valid], check_names=False)
        pd.testing.assert_series_equal(middle[valid], lower[valid], check_names=False)


class TestNegativePeriod:
    """Negative or zero periods should raise ValueError."""

    def test_sma_zero_period(self) -> None:
        with pytest.raises(ValueError):
            sma(pd.Series([1.0, 2.0, 3.0]), period=0)

    def test_ema_negative_period(self) -> None:
        with pytest.raises(ValueError):
            ema(pd.Series([1.0, 2.0, 3.0]), period=-1)


class TestATREdgeCases:
    """Edge cases for Average True Range."""

    def test_atr_basic(self) -> None:
        high = pd.Series([105.0, 106.0, 107.0, 108.0] * 5)
        low = pd.Series([95.0, 96.0, 97.0, 98.0] * 5)
        close = pd.Series([100.0, 101.0, 102.0, 103.0] * 5)
        result = atr(high, low, close, period=5)
        assert len(result) == 20
        assert not result.iloc[-1:].isna().any()

    def test_atr_constant_range(self) -> None:
        """When high-low is constant, ATR should equal that range."""
        high = pd.Series([110.0] * 20)
        low = pd.Series([90.0] * 20)
        close = pd.Series([100.0] * 20)
        result = atr(high, low, close, period=5)
        valid = result.dropna()
        assert valid.iloc[-1] == pytest.approx(20.0)


class TestVWAPEdgeCases:
    """Edge cases for VWAP."""

    def test_vwap_zero_volume(self) -> None:
        high = pd.Series([101.0, 102.0])
        low = pd.Series([99.0, 98.0])
        close = pd.Series([100.0, 100.0])
        volume = pd.Series([0.0, 0.0])
        result = vwap(high, low, close, volume)
        # 0/0 → NaN
        assert result.isna().all()


class TestOBVEdgeCases:
    """Edge cases for On-Balance Volume."""

    def test_obv_flat_price(self) -> None:
        """When price doesn't change, direction is 0, OBV stays flat."""
        close = pd.Series([100.0] * 5)
        volume = pd.Series([1000.0] * 5)
        result = obv(close, volume)
        assert result.iloc[-1] == pytest.approx(0.0)


# ── Signals: crossover / crossunder edge cases ──────────────────────────


class TestCrossover:
    """Test bullish crossover detection."""

    def test_basic_crossover(self) -> None:
        fast = pd.Series([5, 6, 7, 8, 9, 10])
        slow = pd.Series([8, 8, 8, 8, 8, 8])
        result = crossover(fast, slow)
        # fast crosses above slow at index 3 (fast=8>slow=8 is False, index 4: 9>8, shift check 8<=8)
        assert result.iloc[4] is np.True_

    def test_no_crossover(self) -> None:
        fast = pd.Series([1, 2, 3, 4])
        slow = pd.Series([10, 10, 10, 10])
        result = crossover(fast, slow)
        assert not result.any()

    def test_already_above(self) -> None:
        """Fast always above slow → no crossover."""
        fast = pd.Series([20, 21, 22, 23])
        slow = pd.Series([10, 10, 10, 10])
        result = crossover(fast, slow)
        assert not result.any()

    def test_crossover_empty(self) -> None:
        fast = pd.Series([], dtype=float)
        slow = pd.Series([], dtype=float)
        result = crossover(fast, slow)
        assert len(result) == 0

    def test_crossover_single_point(self) -> None:
        fast = pd.Series([10.0])
        slow = pd.Series([5.0])
        result = crossover(fast, slow)
        # shift(1) is NaN → False
        assert not result.any()

    def test_crossover_nan_values(self) -> None:
        fast = pd.Series([np.nan, 5.0, 10.0, 15.0])
        slow = pd.Series([np.nan, 8.0, 8.0, 8.0])
        result = crossover(fast, slow)
        # Should handle NaN gracefully
        assert len(result) == 4

    def test_exact_touch_is_not_crossover(self) -> None:
        """When fast == slow exactly, it's not a crossover (need > not >=)."""
        fast = pd.Series([5, 8, 8, 8])
        slow = pd.Series([8, 8, 8, 8])
        result = crossover(fast, slow)
        assert not result.any()


class TestCrossunderEdgeCases:
    """Extended crossunder edge cases."""

    def test_crossunder_empty(self) -> None:
        result = crossunder(pd.Series([], dtype=float), pd.Series([], dtype=float))
        assert len(result) == 0

    def test_crossunder_single_point(self) -> None:
        result = crossunder(pd.Series([5.0]), pd.Series([10.0]))
        assert not result.any()

    def test_always_below(self) -> None:
        fast = pd.Series([1, 2, 3, 4])
        slow = pd.Series([10, 10, 10, 10])
        result = crossunder(fast, slow)
        assert not result.any()
