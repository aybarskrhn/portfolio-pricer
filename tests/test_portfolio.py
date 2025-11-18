import pandas as pd

from portfolio_pricer import Portfolio


def test_portfolio_basic_pl_and_weights():
    df = pd.DataFrame(
        [
            {"ticker": "AAA", "quantity": 10, "avg_cost": 100.0, "latest_price": 110.0},
            {"ticker": "BBB", "quantity": 5, "avg_cost": 200.0, "latest_price": 180.0},
        ]
    )

    portfolio = Portfolio.from_dataframe(df)
    analytics = portfolio.to_dataframe()

    # Check cost basis and market values
    a = analytics.loc[analytics["ticker"] == "AAA"].iloc[0]
    b = analytics.loc[analytics["ticker"] == "BBB"].iloc[0]

    assert a["cost_basis"] == 1000.0
    assert a["market_value"] == 1100.0
    assert b["cost_basis"] == 1000.0
    assert b["market_value"] == 900.0

    # Check P&L
    assert a["unrealized_pl"] == 100.0
    assert b["unrealized_pl"] == -100.0

    # Total portfolio values
    assert portfolio.total_cost_basis == 2000.0
    assert portfolio.total_market_value == 2000.0
    assert portfolio.total_unrealized_pl == 0.0
    assert portfolio.total_unrealized_pl_pct == 0.0

    # Weights should both be ~50%
    weights = analytics.set_index("ticker")["weight_pct"]
    assert abs(weights["AAA"] - 50.0) < 1e-6
    assert abs(weights["BBB"] - 50.0) < 1e-6


