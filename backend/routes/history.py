from fastapi import APIRouter
from services.data_service import get_stock_data

router = APIRouter()


@router.get("/history/{ticker}")
def get_history(ticker: str, n: int = 10):  # notice the n is used as query parameter

    data = get_stock_data(ticker)

    if data.empty:
        return {'error': "Invalid Ticker Provided"}

    # data dataframe has this columns
    data = data[["Open", "High", "Low", "Close"]]
    n = min(n, 50)
    data = data.tail(n)     # last n data rows

    # convert to JSON-Friendly format
    result = []

    for index, row in data.iterrows():  # understand the syntax index is datetime
        result.append({
            "date": str(index.date()),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2)
        })
    return result
