## Portfolio Pricer (Student Project)

A small but complete **portfolio pricing & analytics tool** built in Python.
It ingests a simple holdings file, pulls **live market data** from Yahoo Finance,
and produces **P&L, weights, and basic risk metrics** at both position and portfolio level.

Designed to be a clear, realistic project to showcase skills for **investment banking** and **consulting** internships:

- **Financial logic**: cost basis, market value, unrealized P&L, position weights.
- **Risk awareness**: historical volatility and portfolio-level volatility.
- **Automation**: turns a manual Excel-style workflow into a repeatable tool.
- **Communication**: CLI + dashboard + documentation aimed at non-developers.

---

### Install

From the project root (`/Users/aybarskarahan/Documents/Projects/portfolio_pricer`):

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

### Input format

Use a CSV with at least the following columns:

- **ticker**: e.g. `AAPL`
- **quantity**: number of shares/units
- **avg_cost**: average cost per share (in your base currency)

Example (`examples/sample_portfolio.csv`):

```text
ticker,quantity,avg_cost
AAPL,10,150
MSFT,5,210
TSLA,2,600
```

---

### Using the CLI

Run from the project root after installing dependencies:

```bash
python -m portfolio_pricer.cli --file examples/sample_portfolio.csv
```

Options:

- **`--file` / `-f`**: path to your holdings CSV.
- **`--output` / `-o`**: where to save the analytics CSV (default: `portfolio_pricer_output.csv`).
- **`--risk-period`**: lookback for risk metrics (e.g. `6mo`, `1y`, `2y`).

The CLI will:

- Fetch latest prices and basic metadata (e.g. sector) from Yahoo Finance.
- Compute per-position:
  - Market value
  - Cost basis
  - Unrealized P&L (amount and %)
  - Portfolio weight
- Estimate:
  - Annualized volatility per ticker
  - Portfolio-level annualized volatility (using historical covariance and current weights)
- Print a nicely formatted table to the terminal and save a CSV.

---

### Using the Streamlit dashboard

To launch the interactive app:

```bash
streamlit run portfolio_pricer/streamlit_app.py
```

What you get:

- File upload for your holdings CSV.
- Live pricing & P&L by position.
- Portfolio-level KPIs (market value, cost basis, P&L and P&L %).
- Estimated portfolio annualized volatility based on historical returns.
- Charts:
  - Allocation by ticker.
  - Allocation by sector (when available).

This is great for screenshots and demos in interviews.

---

### Running tests

Basic tests (using `pytest`) verify that:

- Cost basis, market value, P&L and weights are calculated correctly.
- Volatility functions behave as expected.

Run:

```bash
pytest
```

---

### How to talk about this on your CV / in interviews

**Project title (CV)**  
`Portfolio Pricing & Risk Analytics Tool (Python)`

**Example bullet points:**

- **Built** a Python tool that ingests portfolio holdings, fetches live market data (Yahoo Finance) and computes position-level and portfolio-level market value, cost basis and unrealized P&L.
- **Implemented** portfolio analytics including position weights, contribution to total value, and basic risk metrics using historical return data and covariance-based portfolio volatility.
- **Developed** both a command-line interface and a Streamlit dashboard, making the analysis accessible to non-technical users and demonstrating ability to explain financial outputs clearly.

**Talking points for IB / consulting interviews:**

- Emphasize how this replaces repetitive spreadsheet work with an automated process.
- Walk through the logic step-by-step (inputs → data fetch → calculations → outputs).
- Highlight how you separated concerns:
  - data fetching (`data_fetch.py`)
  - core model (`portfolio.py`, `analytics.py`)
  - interfaces (`cli.py`, `streamlit_app.py`)
  - tests & documentation.
- Link the tool to real tasks: quick portfolio health-checks, scenario thinking and risk awareness.


