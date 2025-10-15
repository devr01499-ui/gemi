import subprocess
import json
import sys
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
        python_executable = sys.executable
        script_path = "backend/services/pairs_trade_backtest.py"
        
        command = [
            python_executable,
            script_path,
            "--tickers", request.tickers[0], request.tickers[1],
            "--start", request.start_date,
            "--end", request.end_date
        ]
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise HTTPException(
                status_code=500, 
                detail=f"Backtest script failed: {stderr}"
            )

        json_output_str = stdout[stdout.find('{'):]
        results = json.loads(json_output_str)
        return results

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, 
            detail="Failed to parse JSON output from the backtest script."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
