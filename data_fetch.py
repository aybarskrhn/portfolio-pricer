"""
Data fetching utilities for Portfolio Pricer.

Currently uses `yfinance` as a convenient public source for:
- Latest closing prices
- Historical adjusted prices (for returns / volatility)
- Basic company info (e.g. sector)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import pandas as pd
import yfinance as yf


@dataclass
class TickerInfo:
    """Basic metadata for a single ticker."""

    ticker: str
    sector: Optional[str] = None
    long_name: Optional[str] = None


def fetch_latest_prices(tickers: Iterable[str]) -> Dict[str, float]:
    """
    Fetch the most recent close price for each ticker.

    Returns a dictionary {ticker: price}.
    """

    tickers = list({t.upper() for t in tickers})
    if not tickers:
        return {}

    data = yf.download(tickers, period="2d", interval="1d", threads=True, progress=False)
    # Normalize to DataFrame and take the last available close for each ticker
    close = data["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame()

    latest: Dict[str, float] = {}
    for t in tickers:
        series = close[t].dropna()
        if not series.empty:
            latest[t] = float(series.iloc[-1])
    return latest


def fetch_historical_prices(
    tickers: Iterable[str],
    period: str = "1y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch historical adjusted close prices for the given tickers.

    Returns a DataFrame indexed by date with tickers as columns.
    """
    tickers = list({t.upper() for t in tickers})
    if not tickers:
        return pd.DataFrame()

    data = yf.download(
        tickers,
        period=period,
        interval=interval,
        auto_adjust=True,
        threads=True,
        progress=False,
    )
    adj_close = data["Close"]
    if isinstance(adj_close, pd.Series):
        adj_close = adj_close.to_frame()
    return adj_close.dropna(how="all")


def fetch_ticker_info(tickers: Iterable[str]) -> List[TickerInfo]:
    """
    Fetch basic info (name, sector) for each ticker.
    """
    infos: List[TickerInfo] = []
    for t in {t.upper() for t in tickers}:
        tk = yf.Ticker(t)
        info = tk.info or {}
        sector = info.get("sector")
        long_name = info.get("longName") or info.get("shortName")
        infos.append(TickerInfo(ticker=t, sector=sector, long_name=long_name))
    return infos


