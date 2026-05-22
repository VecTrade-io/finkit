"""VecTrade FinKit — open-source financial computation library."""

__version__ = "0.1.0"

from finkit.costs import TradeCost, annual_cost_drag, calculate_trade_cost
from finkit.indicators import atr, bollinger_bands, ema, macd, obv, rsi, sma, vwap
from finkit.risk import max_drawdown, sharpe_ratio, sortino_ratio, var
from finkit.screen import Rule, screen
from finkit.signals import SignalEngine, crossover, crossunder, divergence

__all__ = [
    # Technical indicators
    "sma",
    "ema",
    "rsi",
    "macd",
    "bollinger_bands",
    "atr",
    "vwap",
    "obv",
    # Signal detection
    "crossover",
    "crossunder",
    "divergence",
    "SignalEngine",
    # Risk metrics
    "sharpe_ratio",
    "sortino_ratio",
    "max_drawdown",
    "var",
    # Stock screening
    "Rule",
    "screen",
    # Cost calculation
    "calculate_trade_cost",
    "annual_cost_drag",
    "TradeCost",
]
