# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-05-29

### Changed

- **Stable release** — all public APIs finalized, semver enforced from this point

## [0.1.0] - 2026-05-15

### Added

- Initial release of FinKit
- Technical indicators: `sma`, `ema`, `rsi`, `macd`, `bollinger_bands`, `atr`, `vwap`, `obv`
- Signal detection: `crossover`, `crossunder`, `divergence`, `SignalEngine`
- Risk metrics: `sharpe_ratio`, `sortino_ratio`, `max_drawdown`, `var`
- Stock screening: `Rule`, `screen` with 9 operators
- Cost analysis: `calculate_trade_cost`, `annual_cost_drag`, `TradeCost`
- 99% test coverage with branch coverage
- CI/CD with GitHub Actions (Python 3.9–3.12)

[Unreleased]: https://github.com/VecTrade-io/finkit/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/VecTrade-io/finkit/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/VecTrade-io/finkit/releases/tag/v0.1.0
