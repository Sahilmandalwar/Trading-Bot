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
    data = stock.history(period = "3mo" )  # cause using last 50 days data

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

@app.get("/history/{ticker}")
def get_history(ticker: str, n : int = 10):  # notice the n is used as query parameter 
    stock = yf.Ticker(ticker)
    data = stock.history(period='1mo')

    if data.empty:
        return {'error' : "Invalid Ticker Provided"}

    data = data[["Open", "High", "Low", "Close"]] # data dataframe has this columns
    n =  min(n, 50)
    data = data.tail(n)     # last n data rows

    # convert to JSON-Friendly format
    result = []

    for index, row in data.iterrows():  # understand the syntax index is datetime 
        result.append({
            "date" : str(index.date()),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2)
        })
    return result

@app.get('/backtest/{ticker}')
def backtest(ticker: str, mode: str = 'full'):
    stock = yf.Ticker(ticker)
    original_data = stock.history(period='6mo', interval='1d')

    if original_data.empty:
        return {'error': "Invalid Ticker Provided"}

    data = original_data.copy()
    

    data['MA20'] = data["Close"].rolling(20).mean()  # works like sliding window
    data['MA50'] = data['Close'].rolling(50).mean()

    data = data.dropna()

    position = 0  # 0 mean no stock , 1 mean holding
    profit = 0
    buy_price = 0
    trades = 0
    wins = 0
    losses = 0
    holding_days = 0

    trade_log = []
    prev_row = {}

    trend_window = 0

    for _, row in data.iterrows():

        if mode == 'basic': 
            if row['MA20'] > row['MA50']:
                buy_price = row['Close']
                position = 1
            elif row['MA20'] < row['MA50']:
                position = 0
                trade_profit = row['Close'] - buy_price
                profit += trade_profit

                if trade_profit > 0:
                    wins += 1
                else:
                    losses += 1
                trades += 1

                trade_log.append({
                    "buy": round(buy_price, 2),
                    "sell": round(row["Close"], 2),
                    "profit": round(trade_profit, 2)
                })
           
        elif mode == 'strength':
            strength = (row['MA20'] - row['MA50']) / row['MA50']
            if strength > 0 and position == 0:
                buy_price = row["Close"]
                position = 1
            elif strength < 0 and position == 1:
                position = 0
                trade_profit = row['Close'] - buy_price
                profit += trade_profit

                if trade_profit > 0:
                    wins += 1
                else:
                    losses += 1
                trades += 1

                trade_log.append({
                    "buy": round(buy_price, 2),
                    "sell": round(row["Close"], 2),
                    "profit": round(trade_profit, 2)
                })


        elif mode == 'full':
            strength = (row['MA20'] - row['MA50']) / row['MA50']
            prev_strength = 0

            if len(prev_row) != 0:
                prev_strength = (prev_row['MA20'] - prev_row['MA50']) / prev_row['MA50']


            crossover = prev_strength <= 0 and strength > 0
            strong_trend = strength > 0.003

            if crossover:
                trend_window = 7
            elif trend_window > 0:
                trend_window -= 1

            if (crossover or trend_window > 0) and strong_trend and position == 0:
                buy_price = row['Close']
                position = 1
                holding_days = 0

            elif strength < -0.003 and position == 1 and holding_days > 3:
                position = 0
                trade_profit = row['Close'] - buy_price
                profit += trade_profit

                if trade_profit > 0:
                    wins += 1
                else:
                    losses += 1
                trades += 1

                trade_log.append({
                    "buy" : round(buy_price,2),
                    "sell" : round(row["Close"],2),
                    "profit" : round(trade_profit,2) 
                })

            elif  position == 1 and row["Close"] < buy_price * 0.97:
                position = 0
                trade_profit = row['Close'] - buy_price
                profit += trade_profit

                if trade_profit > 0:
                    wins += 1
                else:
                    losses += 1
                trades += 1

                trade_log.append({
                    "buy": round(buy_price, 2),
                    "sell": round(row["Close"], 2),
                    "profit": round(trade_profit, 2)
                })
            
            if position == 1:
                holding_days += 1

            prev_row['MA20'] = row['MA20']
            prev_row['MA50'] = row['MA50']

            
    if position == 1:
        trade_profit = data.iloc[-1]['Close'] - buy_price
        profit += trade_profit
        trades += 1
        if trade_profit > 0:
            wins += 1
        else:
            losses += 1
            
        trade_log.append({
            "buy": round(buy_price, 2),
            "sell": round(data.iloc[-1]["Close"], 2),
            "profit": round(trade_profit, 2)
        })

    win_rate = (wins / trades * 100) if trades > 0 else 0
        
    return {
        "ticker": ticker.upper(),
        "total_profit": round(profit, 2),
        "total_trades": trades,
        "wins": wins,
        "losses": losses,
        "win_rate" : win_rate,
        "trade_log" : trade_log
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





