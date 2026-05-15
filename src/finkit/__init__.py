"""VecTrade FinKit — open-source financial computation library."""

__version__ = "0.1.0"

from finkit.indicators import sma, ema, rsi, macd, bollinger_bands, atr, vwap, obv
from finkit.signals import crossover, crossunder, divergence, SignalEngine
from finkit.risk import sharpe_ratio, sortino_ratio, max_drawdown, var
from finkit.screen import Rule, screen
from finkit.costs import calculate_trade_cost, annual_cost_drag, TradeCost

__all__ = [
    # Technical indicators
    "sma", "ema", "rsi", "macd", "bollinger_bands", "atr", "vwap", "obv",
    # Signal detection
    "crossover", "crossunder", "divergence", "SignalEngine",
    # Risk metrics
    "sharpe_ratio", "sortino_ratio", "max_drawdown", "var",
    # Stock screening
    "Rule", "screen",
    # Cost calculation
    "calculate_trade_cost", "annual_cost_drag", "TradeCost",
]
