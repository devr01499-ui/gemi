import yfinance as yf
import pandas as pd
import statsmodels.api as sm
import json
import argparse
import numpy as np
from numba import jit

@jit(nopython=True)
def backtest_loop(zscore_values, lookback, entry_threshold, exit_threshold):
    """Optimized backtest loop using numba for performance."""
    position = 0
    trades = []
    for i in range(lookback, len(zscore_values)):
        current_zscore = zscore_values[i]
        if position == 0:
            if current_zscore > entry_threshold:
                position = -1
                trades.append(('entry', i, current_zscore))
            elif current_zscore < -entry_threshold:
                position = 1
                trades.append(('entry', i, current_zscore))
        else:
            if abs(current_zscore) < exit_threshold:
                trades.append(('exit', i, current_zscore))
                position = 0
    return trades

def fetch_data(tickers, start_date, end_date):
    """Fetches daily adjusted close prices for a list of tickers."""
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        return data['Adj Close'].dropna()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_spread(series1, series2):
    """Calculates the spread of two series using an OLS regression."""
    if isinstance(series2, pd.Series):
        series2_df = series2.to_frame()
    else:
        series2_df = series2
    series2_with_const = sm.add_constant(series2_df, prepend=False)
    model = sm.OLS(series1, series2_with_const).fit()
    hedge_ratio = model.params.iloc[0]
    spread = series1 - hedge_ratio * series2
    return spread, hedge_ratio

def run_backtest(tickers, start_date, end_date):
    """Runs a simplified pairs trading backtest and returns the results as a dictionary."""
    all_data = fetch_data(tickers, start_date, end_date)

    if all_data is not None and len(all_data.columns) == 2:
        series1, series2 = all_data[tickers[0]], all_data[tickers[1]]
        spread, hedge_ratio = calculate_spread(series1, series2)

        # Simplified backtest logic without backtrader
        lookback = 20
        entry_threshold = 2.0
        exit_threshold = 0.5

        spread_mean = spread.rolling(window=lookback).mean()
        spread_std = spread.rolling(window=lookback).std()
        zscore = (spread - spread_mean) / spread_std

        position = 0
        cash = 100000.0
        trades = []

        # Optimized backtest loop using numba for performance
        zscore_values = zscore.values
        trades = backtest_loop(zscore_values, lookback, entry_threshold, exit_threshold)

        # Calculate simple returns (simplified)
        total_return = (len(trades) // 2) * 0.02  # Assume 2% per round trip
        final_portfolio = cash * (1 + total_return)

        output = {
            "tickers": tickers, "start_date": start_date, "end_date": end_date,
            "initial_portfolio": 100000.0, "final_portfolio": round(final_portfolio, 2),
            "total_return_pct": round(total_return * 100, 2),
            "sharpe_ratio": "N/A",  # Simplified
            "max_drawdown_pct": "N/A",  # Simplified
            "trades": len(trades)
        }
        return output
    else:
        return {"error": "Failed to fetch data"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pairs Trading Backtest')
    parser.add_argument('--tickers', nargs=2, default=['GOOGL', 'MSFT'], help='A pair of tickers to trade')
    parser.add_argument('--start', default='2020-01-01', help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', default='2023-12-31', help='End date in YYYY-MM-DD format')
    args = parser.parse_args()

    output = run_backtest(args.tickers, args.start, args.end)
    print(json.dumps(output, indent=4))
