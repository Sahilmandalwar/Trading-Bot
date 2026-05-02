
def run_backtest(data, mode='full'):

    position = 0  # 0 mean no stock , 1 mean holding
    profit = 0
    buy_price = 0
    trades = 0
    wins = 0
    losses = 0
    holding_days = 0
    max_price = 0

    trade_log = []
    prev_row = {}

    momentum = 0

    trend_window = 0

    def sell_stock():
        nonlocal position, profit, trades, wins, losses, holding_days

        position = 0
        trade_profit = row['Close'] - buy_price
        profit += trade_profit
        holding_days = 0

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

    for _, row in data.iterrows():

        if mode == 'basic':
            if row['MA20'] > row['MA50'] and position == 0:
                buy_price = row['Close']
                position = 1

            elif row['MA20'] < row['MA50'] and position == 1:
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
               sell_stock()

        elif mode == 'full':
            strength = (row['MA20'] - row['MA50']) / row['MA50']
            prev_strength = 0

            if len(prev_row) != 0:
                prev_strength = (prev_row['MA20'] -
                                 prev_row['MA50']) / prev_row['MA50']
                momentum = (row["Close"] - prev_row["Close"]) / prev_row["Close"]
            

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
                max_price = buy_price

            elif position == 1 and row["Close"] < max_price * 0.97:
                sell_stock()

            elif position == 1 and momentum < -0.002 and holding_days > 2:
                sell_stock()
            elif position == 1 and holding_days > 5 and row["Close"] <= buy_price:
                sell_stock()
            elif strength < -0.003 and position == 1 and holding_days > 2:
                sell_stock()

            if position == 1:
                holding_days += 1
                max_price = max(max_price, row["Close"])

            prev_row = row



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
        "total_profit": round(profit, 2),
        "total_trades": trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "trade_log": trade_log
    }
