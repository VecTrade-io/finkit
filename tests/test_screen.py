"""Tests for FinKit stock screener."""

import pandas as pd
import pytest

from finkit.screen import Rule, screen


@pytest.fixture
def universe() -> pd.DataFrame:
    """Sample stock universe for screening."""
    return pd.DataFrame(
        {
            "symbol": ["AAPL", "GOOGL", "MSFT", "AMZN", "META"],
            "market_cap": [3.1e12, 2.1e12, 3.0e12, 1.9e12, 1.3e12],
            "pe_ratio": [28.5, 25.0, 32.0, 55.0, 23.0],
            "dividend_yield": [0.005, 0.0, 0.007, 0.0, 0.0],
            "sector": [
                "Technology",
                "Technology",
                "Technology",
                "Consumer",
                "Technology",
            ],
            "volume": [45e6, 28e6, 35e6, 50e6, 20e6],
        }
    )


class TestScreen:
    """Test rule-based stock screening."""

    def test_single_rule_gt(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="market_cap", operator="gt", value=2e12)]
        result = screen(universe, rules)
        assert len(result) == 3
        assert set(result["symbol"]) == {"AAPL", "GOOGL", "MSFT"}

    def test_single_rule_lt(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="pe_ratio", operator="lt", value=30)]
        result = screen(universe, rules)
        assert "AAPL" in result["symbol"].values
        assert "GOOGL" in result["symbol"].values
        assert "META" in result["symbol"].values
        assert "AMZN" not in result["symbol"].values

    def test_single_rule_eq(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="sector", operator="eq", value="Consumer")]
        result = screen(universe, rules)
        assert len(result) == 1
        assert result.iloc[0]["symbol"] == "AMZN"

    def test_multiple_rules_and(self, universe: pd.DataFrame) -> None:
        """Multiple rules are ANDed together."""
        rules = [
            Rule(field="market_cap", operator="gt", value=2e12),
            Rule(field="pe_ratio", operator="lt", value=30),
        ]
        result = screen(universe, rules)
        assert set(result["symbol"]) == {"AAPL", "GOOGL"}

    def test_empty_result(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="pe_ratio", operator="lt", value=1)]
        result = screen(universe, rules)
        assert len(result) == 0

    def test_no_rules_returns_all(self, universe: pd.DataFrame) -> None:
        result = screen(universe, [])
        assert len(result) == len(universe)

    def test_gte_operator(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="pe_ratio", operator="gte", value=28.5)]
        result = screen(universe, rules)
        assert "AAPL" in result["symbol"].values
        assert "MSFT" in result["symbol"].values
        assert "AMZN" in result["symbol"].values

    def test_ne_operator(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="sector", operator="ne", value="Technology")]
        result = screen(universe, rules)
        assert len(result) == 1
        assert result.iloc[0]["symbol"] == "AMZN"

    def test_lte_operator(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="pe_ratio", operator="<=", value=25.0)]
        result = screen(universe, rules)
        assert set(result["symbol"]) == {"GOOGL", "META"}

    def test_lte_operator_alias(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="pe_ratio", operator="lte", value=25.0)]
        result = screen(universe, rules)
        assert set(result["symbol"]) == {"GOOGL", "META"}

    def test_between_operator(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="pe_ratio", operator="between", value=(24, 30))]
        result = screen(universe, rules)
        assert set(result["symbol"]) == {"AAPL", "GOOGL"}

    def test_in_operator(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="symbol", operator="in", value=["AAPL", "META"])]
        result = screen(universe, rules)
        assert set(result["symbol"]) == {"AAPL", "META"}

    def test_contains_operator(self, universe: pd.DataFrame) -> None:
        rules = [Rule(field="sector", operator="contains", value="tech")]
        result = screen(universe, rules)
        assert len(result) == 4  # All Technology stocks

    def test_field_not_in_columns(self, universe: pd.DataFrame) -> None:
        """Rule with a field not in the DataFrame is silently skipped."""
        rules = [Rule(field="nonexistent", operator="gt", value=0)]
        result = screen(universe, rules)
        assert len(result) == len(universe)

    def test_eq_symbol_operator(self, universe: pd.DataFrame) -> None:
        """Test == operator symbol variant."""
        rules = [Rule(field="sector", operator="==", value="Consumer")]
        result = screen(universe, rules)
        assert len(result) == 1

    def test_ne_symbol_operator(self, universe: pd.DataFrame) -> None:
        """Test != operator symbol variant."""
        rules = [Rule(field="sector", operator="!=", value="Technology")]
        result = screen(universe, rules)
        assert len(result) == 1
