from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request  # notice how FastAPI written
import yfinance as yf

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


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "message": "Route not found",
            "path": str(request.url)
        }
    )


"""
    code summary: 
        imported fastapi , yfinance
        route create and added functionality
        stock hold the data of ticker 
        data holds history of stock for certain interval
        return the latest price and ticker name in json format
        code run through 
"""



