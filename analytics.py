"""
Analytical helpers for portfolio risk/return.
"""

from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd


def compute_daily_returns(price_history: pd.DataFrame) -> pd.DataFrame:
    """
    Convert a DataFrame of prices into daily percentage returns.
    """
    if price_history.empty:
        return pd.DataFrame()
    returns = price_history.sort_index().pct_change().dropna(how="all")
    return returns


def annualized_volatility(
    returns: pd.DataFrame,
    trading_days: int = 252,
) -> pd.Series:
    """
    Compute annualized volatility for each column of returns.
    """
    if returns.empty:
        return pd.Series(dtype=float)
    daily_vol = returns.std()
    return daily_vol * np.sqrt(trading_days)


def portfolio_volatility(
    returns: pd.DataFrame,
    weights: Iterable[float],
    trading_days: int = 252,
) -> Optional[float]:
    """
    Compute annualized portfolio volatility given a return matrix and weights.
    """
    if returns.empty:
        return None
    w = np.array(list(weights), dtype=float)
    if returns.shape[1] != len(w):
        raise ValueError("Number of weights must match number of columns in returns.")
    cov = returns.cov()
    daily_var = float(np.dot(w.T, np.dot(cov.values, w)))
    if daily_var < 0:
        return None
    return float(np.sqrt(daily_var) * np.sqrt(trading_days))


