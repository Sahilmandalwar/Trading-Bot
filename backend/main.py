from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request  # notice how FastAPI written
import yfinance as yf
import pandas as pd

app = FastAPI()  # FastAPI object created


@app.get("/")    # home route
def home():
    return {"message": "Trading bot API running..."}


@app.get("/price/{ticker}")  # get current price for ticker
def get_price(ticker: str):
    stock = yf.Ticker(ticker)       # ticker object initiated
    # recorded history of stock of last day notice period="1d"   provide dataframe
    data = stock.history(period="1d")

    if data.empty:          # if data is empty it mean ticker not found
        return {"error": "Invalid ticker provided..."}

    # among the data latest price is found notice C in Close
    latest_price = round(data['Close'].iloc[-1], 2)

    return {        # json format is returned
        "Ticker": ticker.upper(),   # upper has all lowercase letter
        "Price": latest_price
    }

@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    stock = yf.Ticker(ticker)
    data = stock.history(period = "49d")  # cause using last 50 days data

    if data.empty:
        return {"error" : "Invalid ticker Provided..."}
    
    data['MA20'] = data["Close"].rolling(20).mean()  # works like sliding window
    data['MA50'] = data['Close'].rolling(50).mean()

    latest = data.iloc[-1]

    if pd.isna(latest['MA20']) or pd.isna(latest['MA50']):
        return {"message" : "Insufficient data"}

    difference = latest['MA20'] - latest['MA50']

    # Moving average crossover strategy
    if latest['MA20'] > latest['MA50']:
        signal = "BUY"
    elif latest['MA20'] < latest['MA50']:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "Ticker" : ticker.upper(),
        "Signal" : signal,
        "MA20" : round(latest['MA20'],2),
        "MA50" : round(latest['MA50'],2), 
        "difference" : round(difference,2)
    }

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "message": "Route not found",
            "path": str(request.url)
        }
    )





