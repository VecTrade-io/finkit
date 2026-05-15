# finkit

[![License](https://img.shields.io/github/license/VecTrade-io/finkit)](LICENSE) [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Open-source financial analysis library. Production-grade indicators, signals, and risk metrics.

**No VecTrade account required** — this is a standalone library for the quant/fintech community.

## Installation

```bash
pip install vectrade-finkit
```

## Quick Start

```python
import pandas as pd
import finkit

# Technical Indicators
df["sma_20"] = finkit.sma(df["close"], period=20)
df["rsi"] = finkit.rsi(df["close"], period=14)
macd_line, signal, histogram = finkit.macd(df["close"])
upper, middle, lower = finkit.bollinger_bands(df["close"])

# Signal Detection
df["buy_signal"] = finkit.crossover(df["sma_10"], df["sma_50"])

# Risk Metrics
sharpe = finkit.sharpe_ratio(returns)
mdd = finkit.max_drawdown(equity_curve)
value_at_risk = finkit.var(returns, confidence=0.95)

# Stock Screening
from finkit import Rule, screen

results = screen(universe_df, rules=[
    Rule("pe_ratio", "<", 25),
    Rule("market_cap", ">", 10_000_000_000),
    Rule("rsi_14", "between", (30, 70)),
])
```

## Modules

| Module | Functions |
|--------|-----------|
| `finkit.indicators` | `sma`, `ema`, `rsi`, `macd`, `bollinger_bands` |
| `finkit.signals` | `crossover`, `divergence` |
| `finkit.risk` | `sharpe_ratio`, `sortino_ratio`, `max_drawdown`, `var` |
| `finkit.screen` | `Rule`, `screen` |

## Design Principles

- **Zero API dependency** — works with any pandas DataFrame
- **NumPy vectorized** — fast computation on large datasets
- **Minimal dependencies** — only `numpy` and `pandas`
- **Well-tested** — 95%+ coverage with property-based tests

## Documentation

Full API reference at [docs.vectrade.io/finkit](https://docs.vectrade.io/sdks/finkit).

## License

Apache-2.0
