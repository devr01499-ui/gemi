# VANGUARD Trading System API

A FastAPI-based API for running quantitative trading backtests, specifically designed for pairs trading strategies using historical stock data.

## Features

- **Pairs Trading Backtest**: Execute backtests for pairs of stocks using statistical arbitrage.
- **FastAPI Framework**: Modern, fast web framework for building APIs with automatic interactive documentation.
- **Data Fetching**: Integrates with Yahoo Finance for historical stock prices.
- **Backtesting Engine**: Powered by Backtrader for robust strategy simulation.
- **CORS Enabled**: Supports cross-origin requests for frontend integration.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/devr01499-ui/gemi.git
   cd gemi/vanguard
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the API Server

Start the FastAPI server using Uvicorn:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`.

### API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

### Endpoints

- **GET /**: Check API status.
  - Response: `{"status": "VANGUARD API is running"}`

- **POST /backtest/pairs**: Run a pairs trading backtest.
  - Request Body:
    ```json
    {
      "tickers": ["AAPL", "MSFT"],
      "start_date": "2020-01-01",
      "end_date": "2023-12-31"
    }
    ```
  - Response: Backtest results including portfolio value, returns, Sharpe ratio, and max drawdown.

### Example Usage

Using curl to test the backtest endpoint:

```bash
curl -X POST "http://localhost:8000/backtest/pairs" \
     -H "Content-Type: application/json" \
     -d '{
       "tickers": ["GOOGL", "MSFT"],
       "start_date": "2020-01-01",
       "end_date": "2023-12-31"
     }'
```

## Project Structure

```
vanguard/
├── README.md
├── requirements.txt
├── TODO.md
└── backend/
    ├── main.py                 # FastAPI application
    └── services/
        └── pairs_trade_backtest.py  # Pairs trading strategy and backtest logic
```

## Dependencies

- fastapi: Web framework
- uvicorn: ASGI server
- pydantic: Data validation
- pandas: Data manipulation
- numpy: Numerical computing
- statsmodels: Statistical modeling
- yfinance: Yahoo Finance data
- backtrader: Backtesting framework
- python-dotenv: Environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
