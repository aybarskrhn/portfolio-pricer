"""
Simple CSV input/output helpers for portfolios.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd


PathLike = Union[str, Path]


REQUIRED_COLUMNS = ["ticker", "quantity", "avg_cost"]


def load_portfolio_csv(path: PathLike) -> pd.DataFrame:
    """
    Load a portfolio CSV with at least:
    - ticker
    - quantity
    - avg_cost
    """
    path = Path(path)
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Portfolio CSV is missing required columns: {missing}")
    return df


def save_portfolio_output_csv(df: pd.DataFrame, path: PathLike) -> None:
    """
    Save a portfolio analytics DataFrame to CSV.
    """
    path = Path(path)
    df.to_csv(path, index=False)


