"""
Streamlit dashboard for the Portfolio Pricer.

Run with:
    streamlit run portfolio_pricer/streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from . import Portfolio
from .analytics import annualized_volatility, compute_daily_returns, portfolio_volatility
from .data_fetch import fetch_historical_prices, fetch_latest_prices, fetch_ticker_info


def main() -> None:
    st.set_page_config(page_title="Portfolio Pricer", layout="wide")
    st.title("📈 Portfolio Pricer & Analytics")
    st.write(
        "Upload a simple holdings file and get live pricing, P&L and basic risk metrics.\n"
        "Designed as a clear, student-built tool to showcase analytical thinking."
    )

    uploaded_file = st.file_uploader("Upload portfolio CSV (ticker, quantity, avg_cost)", type=["csv"])

    if uploaded_file is None:
        st.info("Use the sample portfolio to get started.")
        sample_path = Path(__file__).with_suffix("").parent / "examples" / "sample_portfolio.csv"
        st.code(str(sample_path))
        return

    portfolio_df = pd.read_csv(uploaded_file)
    if not {"ticker", "quantity", "avg_cost"}.issubset(portfolio_df.columns):
        st.error("CSV must contain at least: ticker, quantity, avg_cost.")
        return

    tickers = portfolio_df["ticker"].astype(str).str.upper().tolist()
    latest_prices = fetch_latest_prices(tickers)
    info = fetch_ticker_info(tickers)
    info_map = {i.ticker: i for i in info}

    portfolio_df["ticker"] = portfolio_df["ticker"].astype(str).str.upper()
    portfolio_df["latest_price"] = portfolio_df["ticker"].map(latest_prices)
    portfolio_df["sector"] = portfolio_df["ticker"].map(
        lambda t: info_map.get(t).sector if info_map.get(t) else None
    )

    portfolio = Portfolio.from_dataframe(portfolio_df)
    analytics_df = portfolio.to_dataframe()

    # Risk settings
    col1, col2 = st.columns(2)
    with col1:
        risk_period = st.selectbox("Risk lookback period", ["6mo", "1y", "2y"], index=1)
    with col2:
        show_sector = st.checkbox("Group summary by sector", value=True)

    price_history = fetch_historical_prices(tickers, period=risk_period)
    returns = compute_daily_returns(price_history)
    vol = annualized_volatility(returns)
    if not vol.empty:
        analytics_df = analytics_df.merge(
            vol.rename("ann_vol"),
            left_on="ticker",
            right_index=True,
            how="left",
        )

    if "weight_pct" in analytics_df.columns and not returns.empty:
        weights = analytics_df["weight_pct"].fillna(0.0) / 100.0
        aligned_returns = returns[analytics_df["ticker"].tolist()]
        port_vol = portfolio_volatility(aligned_returns, weights)
    else:
        port_vol = None

    # Top-level KPIs
    st.subheader("Portfolio Snapshot")
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Market Value", f"{portfolio.total_market_value:,.0f}")  # type: ignore[arg-type]
    kpi_cols[1].metric("Total Cost Basis", f"{portfolio.total_cost_basis:,.0f}")
    if portfolio.total_unrealized_pl is not None:
        kpi_cols[2].metric("Unrealized P&L", f"{portfolio.total_unrealized_pl:,.0f}")
    if portfolio.total_unrealized_pl_pct is not None:
        kpi_cols[3].metric("Unrealized P&L %", f"{portfolio.total_unrealized_pl_pct:,.2f}%")
    if port_vol is not None:
        st.caption(f"Estimated portfolio annualized volatility: **{port_vol:.2%}**")

    # Tables and charts
    st.subheader("Position Detail")
    st.dataframe(
        analytics_df.set_index("ticker"),
        use_container_width=True,
    )

    if "weight_pct" in analytics_df.columns:
        st.subheader("Allocation by Ticker")
        st.bar_chart(
            data=analytics_df.set_index("ticker")["weight_pct"],
        )

    if show_sector and "sector" in analytics_df.columns:
        st.subheader("Allocation by Sector")
        by_sector = (
            analytics_df.groupby("sector")["market_value"]
            .sum()
            .sort_values(ascending=False)
            .dropna()
        )
        if not by_sector.empty:
            sector_weights = by_sector / by_sector.sum() * 100.0
            st.bar_chart(sector_weights)


if __name__ == "__main__":
    main()


