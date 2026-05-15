"""Signal detection utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd


def crossover(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """Detect bullish crossovers (fast crosses above slow). Returns boolean Series."""
    return (fast > slow) & (fast.shift(1) <= slow.shift(1))


def crossunder(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """Detect bearish crossunders (fast crosses below slow). Returns boolean Series."""
    return (fast < slow) & (fast.shift(1) >= slow.shift(1))


def divergence(price: pd.Series, indicator: pd.Series, window: int = 14) -> pd.Series:
    """Detect bullish divergence (price makes lower low, indicator makes higher low)."""
    price_lows = price.rolling(window).min() == price
    ind_lows = indicator.rolling(window).min() == indicator
    price_trend = price.diff(window) < 0
    ind_trend = indicator.diff(window) > 0
    return price_lows & ind_lows & price_trend & ind_trend


@dataclass
class Signal:
    """A trading signal result."""

    name: str
    direction: str  # "long", "short", "neutral"
    strength: float  # 0.0 to 1.0
    timestamp: str | None = None


@dataclass
class SignalRule:
    """A single rule in the signal engine."""

    name: str
    condition: Callable[[pd.DataFrame], pd.Series]
    direction: str = "long"
    weight: float = 1.0


class SignalEngine:
    """Composable signal engine for combining multiple indicator rules.

    Usage:
        engine = SignalEngine()
        engine.add_rule("rsi_oversold", lambda df: df["rsi"] < 30, direction="long")
        engine.add_rule("macd_cross", lambda df: crossover(df["macd"], df["signal"]), direction="long")
        signals = engine.evaluate(df)
    """

    def __init__(self) -> None:
        self._rules: list[SignalRule] = []

    def add_rule(
        self,
        name: str,
        condition: Callable[[pd.DataFrame], pd.Series],
        *,
        direction: str = "long",
        weight: float = 1.0,
    ) -> SignalEngine:
        """Add a signal rule.

        Args:
            name: Human-readable rule name.
            condition: Function that takes a DataFrame and returns a boolean Series.
            direction: Signal direction ("long" or "short").
            weight: Relative importance weight (0.0 to 1.0).

        Returns:
            Self for method chaining.
        """
        self._rules.append(SignalRule(name=name, condition=condition, direction=direction, weight=weight))
        return self

    def evaluate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Evaluate all rules against a DataFrame.

        Args:
            df: Market data DataFrame with indicators pre-computed.

        Returns:
            DataFrame with columns: signal_score, direction, triggered_rules.
        """
        if not self._rules:
            return pd.DataFrame(index=df.index, columns=["signal_score", "direction", "triggered_rules"])

        long_score = pd.Series(0.0, index=df.index)
        short_score = pd.Series(0.0, index=df.index)
        total_long_weight = sum(r.weight for r in self._rules if r.direction == "long")
        total_short_weight = sum(r.weight for r in self._rules if r.direction == "short")

        triggered: list[pd.Series] = []

        for rule in self._rules:
            mask = rule.condition(df).fillna(False).astype(bool)
            if rule.direction == "long" and total_long_weight > 0:
                long_score += mask.astype(float) * (rule.weight / total_long_weight)
            elif rule.direction == "short" and total_short_weight > 0:
                short_score += mask.astype(float) * (rule.weight / total_short_weight)
            triggered.append(mask.map(lambda x: rule.name if x else ""))

        # Determine direction per row
        direction = pd.Series("neutral", index=df.index)
        direction[long_score > short_score] = "long"
        direction[short_score > long_score] = "short"

        # Composite score
        signal_score = pd.concat([long_score, short_score], axis=1).max(axis=1)

        # Triggered rules as comma-separated string
        triggered_df = pd.concat(triggered, axis=1)
        triggered_rules = triggered_df.apply(lambda row: ",".join(r for r in row if r), axis=1)

        return pd.DataFrame({
            "signal_score": signal_score,
            "direction": direction,
            "triggered_rules": triggered_rules,
        }, index=df.index)
