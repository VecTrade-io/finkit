"""Screening primitives — rule-based stock filtering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class Rule:
    """A single screening rule.

    Args:
        field: Column name in the DataFrame.
        operator: Comparison operator.
        value: Target value(s) for comparison.

    Supported operators:
        - "<", "<=", ">", ">=" — numeric comparison
        - "==" — equality
        - "!=" — inequality
        - "between" — value must be tuple (low, high)
        - "in" — value must be a list
        - "contains" — string contains (case-insensitive)
    """

    field: str
    operator: str
    value: Any


def screen(df: pd.DataFrame, rules: list[Rule]) -> pd.DataFrame:
    """Apply screening rules to a DataFrame and return matching rows.

    Args:
        df: Universe DataFrame with one row per stock.
        rules: List of Rule objects defining the filter criteria.

    Returns:
        Filtered DataFrame containing only rows matching all rules.

    Example:
        >>> from finkit.screen import Rule, screen
        >>> results = screen(universe, rules=[
        ...     Rule("pe_ratio", "<", 25),
        ...     Rule("market_cap", ">", 10_000_000_000),
        ...     Rule("sector", "==", "Technology"),
        ... ])
    """
    mask = pd.Series(True, index=df.index)

    for rule in rules:
        if rule.field not in df.columns:
            continue

        col = df[rule.field]
        op = rule.operator

        if op in ("<", "lt"):
            mask &= col < rule.value
        elif op in ("<=", "lte"):
            mask &= col <= rule.value
        elif op in (">", "gt"):
            mask &= col > rule.value
        elif op in (">=", "gte"):
            mask &= col >= rule.value
        elif op in ("==", "eq"):
            mask &= col == rule.value
        elif op in ("!=", "ne"):
            mask &= col != rule.value
        elif op == "between":
            low, high = rule.value
            mask &= (col >= low) & (col <= high)
        elif op == "in":
            mask &= col.isin(rule.value)
        elif op == "contains":
            mask &= col.str.contains(rule.value, case=False, na=False)

    return df[mask].copy()
