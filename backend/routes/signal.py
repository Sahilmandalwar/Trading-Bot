from fastapi import APIRouter
from utils.indicators import add_moving_averages
from services.data_service import get_stock_data
import pandas as pd


router = APIRouter()


@router.get("/signal/{ticker}")
def get_signal(ticker: str):
    data = get_stock_data(ticker)

    if data.empty:
        return {"error": "Invalid ticker Provided..."}

    data = add_moving_averages(data)

    latest = data.iloc[-1]

    if pd.isna(latest['MA20']) or pd.isna(latest['MA50']):
        return {"message": "Insufficient data"}

    difference = latest['MA20'] - latest['MA50']

    # Moving average crossover strategy
    if latest['MA20'] > latest['MA50']:
        signal = "BUY"
    elif latest['MA20'] < latest['MA50']:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "Ticker": ticker.upper(),
        "Signal": signal,
        "MA20": round(latest['MA20'], 2),
        "MA50": round(latest['MA50'], 2),
        "difference": round(difference, 2)
    }
