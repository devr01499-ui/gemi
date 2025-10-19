import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.services.pairs_trade_backtest import run_backtest
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

# --- Application Initialization ---
app = FastAPI(
    title="VANGUARD Trading System API",
    description="An API for running quantitative trading backtests and strategies.",
    version="1.0.0"
)

# --- CORS Middleware ---
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request Body ---
class BacktestRequest(BaseModel):
    tickers: List[str] = Field(..., min_items=2, max_items=2, example=["AAPL", "AMZN"])
    start_date: str = Field(..., example="2022-01-01")
    end_date: str = Field(..., example="2023-12-31")

# --- API Endpoints ---

@app.get("/", tags=["Status"])
async def read_root():
    """A simple endpoint to check if the API is running."""
    return {"status": "VANGUARD API is running"}

@app.post("/backtest/pairs", tags=["Backtesting"])
async def run_pairs_backtest(request: BacktestRequest):
    """
    Executes the pairs trading backtest script with user-defined parameters.
    """
    try:
        results = run_backtest(request.tickers, request.start_date, request.end_date)
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
