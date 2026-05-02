from fastapi import APIRouter
from services.data_service import get_stock_data

router = APIRouter()


@router.get("/price/{ticker}")  # get current price for ticker
def get_price(ticker: str):
    data = get_stock_data(ticker)

    if data.empty:          # if data is empty it mean ticker not found
        return {"error": "Invalid ticker provided..."}

    # among the data latest price is found notice C in Close
    latest_price = round(data['Close'].iloc[-1], 2)

    return {        # json format is returned
        "Ticker": ticker.upper(),   # upper has all lowercase letter
        "Price": latest_price
    }
