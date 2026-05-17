"""Technical indicators."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, period: int = 20) -> pd.Series:
    """Simple Moving Average."""
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int = 20) -> pd.Series:
    """Exponential Moving Average."""
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    signal_period: int | None = None,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD (line, signal, histogram)."""
    sig = signal_period if signal_period is not None else signal
    fast_ema = ema(series, fast)
    slow_ema = ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, sig)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(
    series: pd.Series, period: int = 20, std_dev: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands (upper, middle, lower)."""
    middle = sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


def atr(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """Average True Range — measures volatility.

    Args:
        high: High prices.
        low: Low prices.
        close: Close prices.
        period: Lookback period.

    Returns:
        ATR series.
    """
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()


def vwap(
    high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series
) -> pd.Series:
    """Volume Weighted Average Price (intraday cumulative).

    Args:
        high: High prices.
        low: Low prices.
        close: Close prices.
        volume: Volume data.

    Returns:
        VWAP series.
    """
    typical_price = (high + low + close) / 3
    cumulative_tp_vol = (typical_price * volume).cumsum()
    cumulative_vol = volume.cumsum()
    return cumulative_tp_vol / cumulative_vol


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume — cumulative volume direction indicator.

    Args:
        close: Close prices.
        volume: Volume data.

    Returns:
        OBV series.
    """
    direction = np.sign(close.diff())
    direction.iloc[0] = 0
    return (volume * direction).cumsum()
