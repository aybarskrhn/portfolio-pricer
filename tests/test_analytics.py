import numpy as np
import pandas as pd

from portfolio_pricer.analytics import (
    annualized_volatility,
    compute_daily_returns,
    portfolio_volatility,
)


def test_compute_daily_returns_and_volatility():
    # Simple price series: steadily increasing
    prices = pd.DataFrame(
        {
            "AAA": [100, 101, 102, 103],
            "BBB": [50, 49, 51, 52],
        }
    )
    rets = compute_daily_returns(prices)
    assert rets.shape[0] == 3
    assert rets.shape[1] == 2

    vol = annualized_volatility(rets, trading_days=252)
    assert {"AAA", "BBB"}.issubset(vol.index)
    assert (vol > 0).all()


def test_portfolio_volatility_dimensions():
    prices = pd.DataFrame(
        {
            "AAA": [100, 101, 102, 103],
            "BBB": [50, 49, 51, 52],
        }
    )
    rets = compute_daily_returns(prices)
    w = np.array([0.6, 0.4])
    vol = portfolio_volatility(rets, w, trading_days=252)
    assert vol is not None
    assert vol > 0


