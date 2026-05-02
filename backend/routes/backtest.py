from fastapi import APIRouter
from services.data_service import get_stock_data
from services.strategy_service import run_backtest
from utils.indicators import add_moving_averages

router = APIRouter()


@router.get("/backtest/{ticker}")
def backtest(ticker: str, mode: str = "full"):
    data = get_stock_data(ticker)

    if data.empty:
        return {"error": "Invalid ticker"}

    data = add_moving_averages(data)
    data = data.dropna()

   
    backtest_result = run_backtest(data, mode) 

    
    return {
        "ticker" : ticker,
        **backtest_result
    }


