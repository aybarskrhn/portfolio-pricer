"""
Core portfolio data structures: Position and Portfolio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

import pandas as pd


@dataclass
class Position:
    """Represents a single holding in a portfolio."""

    ticker: str
    quantity: float
    avg_cost: float
    latest_price: Optional[float] = None
    sector: Optional[str] = None

    @property
    def cost_basis(self) -> float:
        return self.quantity * self.avg_cost

    @property
    def market_value(self) -> Optional[float]:
        if self.latest_price is None:
            return None
        return self.quantity * self.latest_price

    @property
    def unrealized_pl(self) -> Optional[float]:
        if self.market_value is None:
            return None
        return self.market_value - self.cost_basis

    @property
    def unrealized_pl_pct(self) -> Optional[float]:
        if self.unrealized_pl is None or self.cost_basis == 0:
            return None
        return (self.unrealized_pl / self.cost_basis) * 100.0


@dataclass
class Portfolio:
    """A collection of positions plus helper analytics."""

    positions: List[Position] = field(default_factory=list)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "Portfolio":
        """
        Build a Portfolio from a DataFrame with columns:
        - ticker
        - quantity
        - avg_cost
        (optional) latest_price, sector
        """
        positions: List[Position] = []
        for _, row in df.iterrows():
            positions.append(
                Position(
                    ticker=str(row["ticker"]).upper(),
                    quantity=float(row["quantity"]),
                    avg_cost=float(row["avg_cost"]),
                    latest_price=float(row["latest_price"])
                    if "latest_price" in df.columns and pd.notna(row["latest_price"])
                    else None,
                    sector=str(row["sector"]) if "sector" in df.columns and pd.notna(row["sector"]) else None,
                )
            )
        return cls(positions=positions)

    def to_dataframe(self) -> pd.DataFrame:
        """
        Represent the portfolio as a DataFrame with analytics columns.
        """
        rows: List[Dict] = []
        for p in self.positions:
            row = {
                "ticker": p.ticker,
                "quantity": p.quantity,
                "avg_cost": p.avg_cost,
                "cost_basis": p.cost_basis,
                "latest_price": p.latest_price,
                "market_value": p.market_value,
                "unrealized_pl": p.unrealized_pl,
                "unrealized_pl_pct": p.unrealized_pl_pct,
                "sector": p.sector,
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        # Drop analytics columns if prices are missing entirely
        if df["market_value"].notna().any():
            total_value = df["market_value"].fillna(0.0).sum()
            if total_value > 0:
                df["weight_pct"] = (df["market_value"].fillna(0.0) / total_value) * 100.0
        return df

    @property
    def total_cost_basis(self) -> float:
        return sum(p.cost_basis for p in self.positions)

    @property
    def total_market_value(self) -> Optional[float]:
        values = [p.market_value for p in self.positions if p.market_value is not None]
        if not values:
            return None
        return float(sum(values))

    @property
    def total_unrealized_pl(self) -> Optional[float]:
        if self.total_market_value is None:
            return None
        return self.total_market_value - self.total_cost_basis

    @property
    def total_unrealized_pl_pct(self) -> Optional[float]:
        if self.total_unrealized_pl is None or self.total_cost_basis == 0:
            return None
        return (self.total_unrealized_pl / self.total_cost_basis) * 100.0


