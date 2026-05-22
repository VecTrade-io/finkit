"""Tests for cost calculation utilities."""

import pytest

from finkit.costs import annual_cost_drag, calculate_trade_cost


class TestCalculateTradeCost:
    """Test trade cost calculations."""

    def test_flat_commission_only(self) -> None:
        result = calculate_trade_cost(100, 50.0, flat_commission=4.95)
        assert result.commission == 4.95
        assert result.spread_cost == 0.0
        assert result.slippage == 0.0
        assert result.total == 4.95
        assert result.cost_per_share == pytest.approx(0.0495)

    def test_per_share_commission(self) -> None:
        result = calculate_trade_cost(1000, 100.0, commission_per_share=0.005)
        assert result.commission == 5.0
        assert result.total == 5.0

    def test_spread_cost(self) -> None:
        # 10 bps on $100k notional = $10
        result = calculate_trade_cost(1000, 100.0, spread_bps=10.0)
        assert result.spread_cost == pytest.approx(100.0)

    def test_slippage(self) -> None:
        # 5 bps on $100k = $5
        result = calculate_trade_cost(1000, 100.0, slippage_bps=5.0)
        assert result.slippage == pytest.approx(50.0)

    def test_combined_costs(self) -> None:
        result = calculate_trade_cost(
            500,
            200.0,
            flat_commission=9.99,
            spread_bps=5.0,
            slippage_bps=3.0,
        )
        notional = 500 * 200.0
        expected_spread = notional * 5.0 / 10_000
        expected_slippage = notional * 3.0 / 10_000
        expected_total = 9.99 + expected_spread + expected_slippage
        assert result.total == pytest.approx(expected_total)
        assert result.cost_per_share == pytest.approx(expected_total / 500)

    def test_zero_shares(self) -> None:
        result = calculate_trade_cost(0, 100.0, flat_commission=5.0)
        assert result.cost_per_share == 0.0


class TestAnnualCostDrag:
    """Test annual cost drag calculation."""

    def test_typical_case(self) -> None:
        drag = annual_cost_drag(trades_per_year=100, avg_trade_cost=10.0, portfolio_value=100_000)
        assert drag == pytest.approx(0.01)

    def test_zero_portfolio(self) -> None:
        drag = annual_cost_drag(trades_per_year=50, avg_trade_cost=5.0, portfolio_value=0)
        assert drag == 0.0

    def test_low_frequency(self) -> None:
        drag = annual_cost_drag(trades_per_year=12, avg_trade_cost=20.0, portfolio_value=500_000)
        assert drag == pytest.approx(0.00048)
