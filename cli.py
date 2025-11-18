"""
Command line interface for the Portfolio Pricer.

Usage example:
    python -m portfolio_pricer.cli --file examples/sample_portfolio.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table

from . import Portfolio
from .analytics import annualized_volatility, compute_daily_returns, portfolio_volatility
from .data_fetch import fetch_historical_prices, fetch_latest_prices, fetch_ticker_info
from .io_utils import load_portfolio_csv, save_portfolio_output_csv


console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portfolio Pricer CLI")
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        required=True,
        help="Path to portfolio CSV (ticker,quantity,avg_cost).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="portfolio_pricer_output.csv",
        help="Path to save analytics CSV.",
    )
    parser.add_argument(
        "--risk-period",
        type=str,
        default="1y",
        help="Historical period for risk metrics (e.g. 6mo, 1y, 2y).",
    )
    return parser


def _pretty_print_summary(df: pd.DataFrame) -> None:
    table = Table(show_header=True, header_style="bold magenta")
    for col in [
        "ticker",
        "quantity",
        "avg_cost",
        "latest_price",
        "market_value",
        "cost_basis",
        "unrealized_pl",
        "unrealized_pl_pct",
        "weight_pct",
    ]:
        if col in df.columns:
            table.add_column(col)

    for _, row in df.sort_values("market_value", ascending=False).iterrows():
        values = []
        for col in table.columns:
            val = row.get(col.header)
            if isinstance(val, float):
                if "pct" in col.header:
                    values.append(f"{val:,.2f}%")
                else:
                    values.append(f"{val:,.2f}")
            else:
                values.append(str(val))
        table.add_row(*values)
    console.print(table)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    portfolio_df = load_portfolio_csv(args.file)

    # Fetch latest prices and metadata
    tickers = portfolio_df["ticker"].astype(str).str.upper().tolist()
    latest_prices = fetch_latest_prices(tickers)
    info = fetch_ticker_info(tickers)
    info_map = {i.ticker: i for i in info}

    portfolio_df["latest_price"] = portfolio_df["ticker"].str.upper().map(latest_prices)
    portfolio_df["sector"] = portfolio_df["ticker"].str.upper().map(
        lambda t: info_map.get(t).sector if info_map.get(t) else None
    )

    portfolio = Portfolio.from_dataframe(portfolio_df)
    analytics_df = portfolio.to_dataframe()

    # Compute basic risk metrics based on historical data
    price_history = fetch_historical_prices(tickers, period=args.risk_period)
    returns = compute_daily_returns(price_history)
    vol = annualized_volatility(returns)
    if not vol.empty:
        # align and attach vol column
        vol_df = vol.rename("ann_vol")
        analytics_df = analytics_df.merge(
            vol_df,
            left_on="ticker",
            right_index=True,
            how="left",
        )

        # portfolio vol if we have all weights and vols
        if "weight_pct" in analytics_df.columns:
            weights = analytics_df["weight_pct"].fillna(0.0) / 100.0
            aligned_returns = returns[analytics_df["ticker"].tolist()]
            port_vol = portfolio_volatility(aligned_returns, weights)
        else:
            port_vol = None
    else:
        port_vol = None

    # Display summary
    console.rule("[bold]Portfolio Summary")
    _pretty_print_summary(analytics_df)

    console.print()
    console.print(
        f"[bold]Total market value:[/bold] {portfolio.total_market_value:,.2f}"  # type: ignore[arg-type]
    )
    console.print(f"[bold]Total cost basis:[/bold] {portfolio.total_cost_basis:,.2f}")
    if portfolio.total_unrealized_pl is not None:
        console.print(f"[bold]Total unrealized P&L:[/bold] {portfolio.total_unrealized_pl:,.2f}")
    if portfolio.total_unrealized_pl_pct is not None:
        console.print(f"[bold]Total unrealized P&L %:[/bold] {portfolio.total_unrealized_pl_pct:,.2f}%")
    if port_vol is not None:
        console.print(f"[bold]Portfolio annualized volatility:[/bold] {port_vol:,.2%}")

    # Save output
    save_portfolio_output_csv(analytics_df, Path(args.output))
    console.print(f"\n[green]Analytics saved to {args.output}[/green]")


if __name__ == "__main__":
    main()


