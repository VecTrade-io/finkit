"""Tests for signal engine."""

import numpy as np
import pandas as pd
import pytest

from finkit.signals import SignalEngine, crossover, crossunder


class TestCrossunder:
    """Test bearish crossunder detection."""

    def test_crossunder_detected(self) -> None:
        fast = pd.Series([10, 9, 8, 7, 6])
        slow = pd.Series([8, 8, 8, 8, 8])
        result = crossunder(fast, slow)
        # fast starts above slow, crosses below at index 2 (8 < 8 is False, 7 < 8 at idx 3)
        assert result.iloc[3] is np.True_

    def test_no_crossunder(self) -> None:
        fast = pd.Series([10, 11, 12, 13])
        slow = pd.Series([5, 5, 5, 5])
        result = crossunder(fast, slow)
        assert not result.any()


class TestSignalEngine:
    """Test the composable signal engine."""

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            "close": [100, 101, 99, 98, 102, 105, 103, 107],
            "rsi": [45, 50, 28, 25, 55, 65, 60, 72],
            "macd": [0.5, 0.3, -0.2, -0.5, 0.1, 0.4, 0.3, 0.6],
            "signal_line": [0.4, 0.4, 0.2, -0.1, -0.2, 0.1, 0.3, 0.4],
        })

    def test_empty_engine(self, sample_df: pd.DataFrame) -> None:
        engine = SignalEngine()
        result = engine.evaluate(sample_df)
        assert "signal_score" in result.columns
        assert "direction" in result.columns

    def test_single_rule(self, sample_df: pd.DataFrame) -> None:
        engine = SignalEngine()
        engine.add_rule("rsi_oversold", lambda df: df["rsi"] < 30, direction="long")
        result = engine.evaluate(sample_df)
        # RSI < 30 at index 2 and 3
        assert result.loc[2, "signal_score"] == 1.0
        assert result.loc[3, "signal_score"] == 1.0
        assert result.loc[0, "signal_score"] == 0.0

    def test_multiple_rules(self, sample_df: pd.DataFrame) -> None:
        engine = SignalEngine()
        engine.add_rule("rsi_oversold", lambda df: df["rsi"] < 30, direction="long", weight=1.0)
        engine.add_rule("macd_positive", lambda df: df["macd"] > 0, direction="long", weight=1.0)
        result = engine.evaluate(sample_df)
        # At index 0: rsi=45 (no), macd=0.5 (yes) → score = 0.5
        assert result.loc[0, "signal_score"] == pytest.approx(0.5)

    def test_triggered_rules_column(self, sample_df: pd.DataFrame) -> None:
        engine = SignalEngine()
        engine.add_rule("rsi_low", lambda df: df["rsi"] < 30, direction="long")
        result = engine.evaluate(sample_df)
        assert "rsi_low" in result.loc[2, "triggered_rules"]
        assert result.loc[0, "triggered_rules"] == ""

    def test_method_chaining(self) -> None:
        engine = SignalEngine()
        result = engine.add_rule("a", lambda df: df["x"] > 0).add_rule("b", lambda df: df["x"] < 0)
        assert result is engine
        assert len(engine._rules) == 2

    def test_direction_long_vs_short(self, sample_df: pd.DataFrame) -> None:
        engine = SignalEngine()
        engine.add_rule("buy_signal", lambda df: df["rsi"] < 30, direction="long")
        engine.add_rule("sell_signal", lambda df: df["rsi"] > 70, direction="short")
        result = engine.evaluate(sample_df)
        # Index 2: RSI=28 < 30 → long
        assert result.loc[2, "direction"] == "long"
        # Index 7: RSI=72 > 70 → short
        assert result.loc[7, "direction"] == "short"
