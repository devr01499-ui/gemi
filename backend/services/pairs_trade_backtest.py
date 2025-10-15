import backtrader as bt
import yfinance as yf
import pandas as pd
import statsmodels.api as sm
import json
import argparse

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

class PairsTradingStrategy(bt.Strategy):
    """The core pairs trading strategy logic."""
    params = (('spread', None), ('lookback', 20), ('entry_threshold', 2.0), ('exit_threshold', 0.5))

    def __init__(self):
        self.spread = self.p.spread
        spread_mean = self.spread.rolling(window=self.p.lookback).mean()
        spread_std = self.spread.rolling(window=self.p.lookback).std()
        self.zscore = (self.spread - spread_mean) / spread_std
        self.data1_close = self.datas[0].close
        self.data2_close = self.datas[1].close

    def next(self):
        if len(self) <= self.p.lookback: return
        current_date = self.datas[0].datetime.date(0)
        try:
            current_zscore = self.zscore.loc[pd.to_datetime(current_date)]
        except KeyError: return
            
        if not self.position:
            if current_zscore > self.p.entry_threshold:
                self.sell(data=self.datas[0])
                self.buy(data=self.datas[1])
            elif current_zscore < -self.p.entry_threshold:
                self.buy(data=self.datas[0])
                self.sell(data=self.datas[1])
        else:
            if abs(current_zscore) < self.p.exit_threshold:
                self.close(data=self.datas[0])
                self.close(data=self.datas[1])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pairs Trading Backtest')
    parser.add_argument('--tickers', nargs=2, default=['GOOGL', 'MSFT'], help='A pair of tickers to trade')
    parser.add_argument('--start', default='2020-01-01', help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', default='2023-12-31', help='End date in YYYY-MM-DD format')
    args = parser.parse_args()

    all_data = fetch_data(args.tickers, args.start, args.end)
    
    if all_data is not None and len(all_data.columns) == 2:
        series1, series2 = all_data[args.tickers[0]], all_data[args.tickers[1]]
        spread, hedge_ratio = calculate_spread(series1, series2)
        
        cerebro = bt.Cerebro()
        cerebro.adddata(bt.feeds.PandasData(dataname=pd.DataFrame(series1)))
        cerebro.adddata(bt.feeds.PandasData(dataname=pd.DataFrame(series2)))
        cerebro.addstrategy(PairsTradingStrategy, spread=spread)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Years)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        results = cerebro.run()
        
        final_portfolio_value = cerebro.broker.getvalue()
        analysis = results[0].analyzers
        sharpe = analysis.sharpe_ratio.get_analysis()['sharperatio']
        
        output = {
            "tickers": args.tickers, "start_date": args.start, "end_date": args.end,
            "initial_portfolio": 100000.0, "final_portfolio": round(final_portfolio_value, 2),
            "total_return_pct": round(analysis.returns.get_analysis()['rtot'] * 100, 2),
            "sharpe_ratio": round(sharpe, 3) if sharpe is not None else "N/A",
            "max_drawdown_pct": round(analysis.drawdown.get_analysis()['max']['drawdown'], 2)
        }
        print(json.dumps(output, indent=4))
