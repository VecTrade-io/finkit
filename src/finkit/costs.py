"""Trading cost calculations — commissions, spread, slippage."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradeCost:
    """Breakdown of trading costs for a single trade."""

    commission: float
    spread_cost: float
    slippage: float
    total: float
    cost_per_share: float


def calculate_trade_cost(
    shares: int,
    price: float,
    *,
    commission_per_share: float = 0.0,
    flat_commission: float = 0.0,
    spread_bps: float = 0.0,
    slippage_bps: float = 0.0,
) -> TradeCost:
    """Calculate total trading cost for an order.

    Args:
        shares: Number of shares.
        price: Expected execution price.
        commission_per_share: Commission per share (e.g., 0.005 for IBKR).
        flat_commission: Fixed commission per trade.
        spread_bps: Estimated half-spread in basis points.
        slippage_bps: Estimated slippage in basis points.

    Returns:
        TradeCost with itemized costs.
    """
    notional = shares * price
    commission = max(flat_commission, shares * commission_per_share)
    spread_cost = notional * (spread_bps / 10_000)
    slippage = notional * (slippage_bps / 10_000)
    total = commission + spread_cost + slippage
    cost_per_share = total / shares if shares > 0 else 0.0

    return TradeCost(
        commission=commission,
        spread_cost=spread_cost,
        slippage=slippage,
        total=total,
        cost_per_share=cost_per_share,
    )


def annual_cost_drag(
    trades_per_year: int,
    avg_trade_cost: float,
    portfolio_value: float,
) -> float:
    """Calculate annual cost drag as a percentage of portfolio value.

    Args:
        trades_per_year: Estimated number of trades per year.
        avg_trade_cost: Average total cost per trade.
        portfolio_value: Total portfolio value.

    Returns:
        Annual cost drag as a decimal (e.g., 0.005 = 0.5%).
    """
    if portfolio_value <= 0:
        return 0.0
    return (trades_per_year * avg_trade_cost) / portfolio_value
