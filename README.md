# finkit

[![CI](https://github.com/VecTrade-io/finkit/actions/workflows/ci.yml/badge.svg)](https://github.com/VecTrade-io/finkit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/vectrade-finkit)](https://pypi.org/project/vectrade-finkit/)
[![License](https://img.shields.io/github/license/VecTrade-io/finkit)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](https://github.com/VecTrade-io/finkit)

Open-source financial analysis library. Production-grade indicators, signals, risk metrics, screening, and cost analysis — all vectorized with NumPy for maximum performance.

**No API key required. No account needed.** This is a free, standalone library for the quant community.

## Why finkit?

| | finkit | TA-Lib | pandas-ta | backtrader |
|---|:---:|:---:|:---:|:---:|
| Pure Python (no C deps) | ✅ | ❌ | ✅ | ✅ |
| Type-safe (py.typed) | ✅ | ❌ | ❌ | ❌ |
| Signal composition engine | ✅ | ❌ | ❌ | ✅ |
| Stock screener built-in | ✅ | ❌ | ❌ | ❌ |
| Risk metrics (Sharpe, VaR) | ✅ | ❌ | ❌ | ❌ |
| Cost analysis | ✅ | ❌ | ❌ | ❌ |
| Zero config | ✅ | ❌ | ✅ | ❌ |
| Maintained (2024–) | ✅ | ❌ | ⚠️ | ❌ |

**finkit gives you everything in one package** — indicators, signals, risk, screening, and cost analysis — with zero native dependencies and full type safety.

## Installation

```bash
pip install vectrade-finkit
```

## Quick Start

```python
import pandas as pd
import finkit

# ── Technical Indicators ──
df["sma_20"] = finkit.sma(df["close"], period=20)
df["ema_12"] = finkit.ema(df["close"], period=12)
df["rsi"] = finkit.rsi(df["close"], period=14)
macd_line, signal, histogram = finkit.macd(df["close"])
upper, middle, lower = finkit.bollinger_bands(df["close"])
df["atr"] = finkit.atr(df["high"], df["low"], df["close"], period=14)
df["vwap"] = finkit.vwap(df["high"], df["low"], df["close"], df["volume"])
df["obv"] = finkit.obv(df["close"], df["volume"])

# ── Signal Detection ──
df["buy_signal"] = finkit.crossover(df["sma_10"], df["sma_50"])
df["sell_signal"] = finkit.crossunder(df["sma_10"], df["sma_50"])
df["divergence"] = finkit.divergence(df["close"], df["rsi"])

# ── Signal Engine (composable rules) ──
engine = finkit.SignalEngine()
engine.add_rule("rsi_oversold", lambda df: df["rsi"] < 30, direction="long")
engine.add_rule("macd_cross", lambda df: finkit.crossover(df["macd"], df["signal"]), direction="long")
signals = engine.evaluate(df)

# ── Risk Metrics ──
sharpe = finkit.sharpe_ratio(returns, risk_free_rate=0.04)
sortino = finkit.sortino_ratio(returns)
mdd = finkit.max_drawdown(equity_curve)
value_at_risk = finkit.var(returns, confidence=0.95)

# ── Stock Screening ──
from finkit import Rule, screen

results = screen(universe_df, rules=[
    Rule("pe_ratio", "<", 25),
    Rule("market_cap", ">", 10_000_000_000),
    Rule("rsi_14", "between", (30, 70)),
    Rule("sector", "in", ["Technology", "Healthcare"]),
])

# ── Cost Analysis ──
cost = finkit.calculate_trade_cost(shares=100, price=150.0, commission_per_share=0.005)
drag = finkit.annual_cost_drag(trades_per_year=200, avg_trade_cost=cost.total, portfolio_value=100_000)
```

## API Reference

### `finkit.indicators`

| Function | Signature | Description |
|----------|-----------|-------------|
| `sma` | `(series, period=20)` | Simple Moving Average |
| `ema` | `(series, period=20)` | Exponential Moving Average |
| `rsi` | `(series, period=14)` | Relative Strength Index (0–100) |
| `macd` | `(series, fast=12, slow=26, signal=9)` | MACD → `(line, signal, histogram)` |
| `bollinger_bands` | `(series, period=20, std_dev=2.0)` | Bollinger → `(upper, middle, lower)` |
| `atr` | `(high, low, close, period=14)` | Average True Range (volatility) |
| `vwap` | `(high, low, close, volume)` | Volume Weighted Average Price |
| `obv` | `(close, volume)` | On-Balance Volume |

### `finkit.signals`

| Function | Signature | Description |
|----------|-----------|-------------|
| `crossover` | `(fast, slow)` | Bullish crossover detection (boolean Series) |
| `crossunder` | `(fast, slow)` | Bearish crossunder detection (boolean Series) |
| `divergence` | `(price, indicator, window=14)` | Bullish divergence detection |
| `SignalEngine` | class | Composable rule-based signal scoring engine |

### `finkit.risk`

| Function | Signature | Description |
|----------|-----------|-------------|
| `sharpe_ratio` | `(returns, risk_free_rate=0.0, periods=252)` | Annualized Sharpe Ratio |
| `sortino_ratio` | `(returns, risk_free_rate=0.0, periods=252)` | Sortino Ratio (downside only) |
| `max_drawdown` | `(returns)` | Maximum peak-to-trough drawdown |
| `var` | `(returns, confidence=0.95, method="historical")` | Value at Risk (historical or parametric) |

### `finkit.screen`

| Function | Signature | Description |
|----------|-----------|-------------|
| `Rule` | `(field, operator, value)` | Screening rule definition |
| `screen` | `(df, rules)` | Apply rules and return matching rows |

**Supported operators:** `<`, `<=`, `>`, `>=`, `==`, `!=`, `between`, `in`, `contains`

### `finkit.costs`

| Function | Signature | Description |
|----------|-----------|-------------|
| `calculate_trade_cost` | `(shares, price, *, commission_per_share, ...)` | Total trade cost breakdown |
| `annual_cost_drag` | `(trades_per_year, avg_trade_cost, portfolio_value)` | Annualized cost as portfolio drag |
| `TradeCost` | dataclass | Structured cost result |

## Design Principles

- **Zero API dependency** — works with any pandas DataFrame
- **NumPy vectorized** — fast computation on large datasets
- **Minimal dependencies** — only `numpy` and `pandas`
- **Fully typed** — `py.typed` marker, works with mypy/pyright
- **Well-tested** — 99% branch coverage

## Use Cases

- **Algorithmic trading** — build signal engines and backtest strategies
- **Portfolio analytics** — Sharpe, Sortino, drawdown, VaR for any portfolio
- **Stock screening** — filter universes of 5,000+ stocks in milliseconds
- **Jupyter notebooks** — quick technical analysis with pandas integration
- **Production pipelines** — ETL-friendly, typed outputs, no side effects
- **Education** — clean API to teach technical analysis concepts

## Community

- 💬 [Discord](https://discord.gg/vectrade) — questions, showcase, discussion
- 🐛 [Issues](https://github.com/VecTrade-io/finkit/issues) — bug reports & feature requests
- 📖 [Docs](https://docs.vectrade.io/sdks/finkit) — full API reference
- ⭐ Star this repo to help others discover it!

## Part of the VecTrade Ecosystem

| Package | Description |
|---------|-------------|
| [`vectrade`](https://github.com/VecTrade-io/vectrade-python) | Python SDK for VecTrade API |
| [`@vectrade/sdk`](https://github.com/VecTrade-io/vectrade-node) | TypeScript/Node SDK |
| [`vectrade-finkit`](https://github.com/VecTrade-io/finkit) | Financial computation library (this package) |
| [`@vectrade/ai-provider`](https://github.com/VecTrade-io/vectrade-ai-provider) | Vercel AI SDK provider |

## Documentation

Full documentation is available at [docs.vectrade.io/sdks/finkit](https://docs.vectrade.io/sdks/finkit).

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

Found finkit useful? Please ⭐ star the repo — it helps others discover the project.

## License

Apache-2.0 — see [LICENSE](LICENSE).
