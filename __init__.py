"""
Portfolio Pricer
----------------

A small Python toolkit to:
- Ingest a portfolio of tickers, quantities, and average costs
- Fetch latest prices from Yahoo Finance
- Compute position-level and portfolio-level P&L and weights
- Run basic risk/return analytics

Intended as a clear, well-structured student project suitable for
investment banking / consulting internship applications.
"""

from .portfolio import Position, Portfolio

__all__ = ["Position", "Portfolio"]


