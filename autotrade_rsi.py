
import pyupbit
import time
import pandas as pd
from datetime import datetime

access = "ZmpwaxjTwBgSZa6Ph1gTx02s1CihnGLP9b5gJmup"
secret = "vkcxaPzDjtmNxb29lgMMSGCBtJZ0ZE99X8bE2Fxj"
upbit = pyupbit.Upbit(access, secret)

ticker = "KRW-BTC"

def log_trade(action, price, volume):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[now, action, price, volume]], columns=["시간", "구분", "가격", "수량"])
    df.to_csv("trading_log.csv", mode='a', header=False, index=False)
    print(f"[{action}] {price}원 | 수량: {volume:.6f} 저장 완료 ✅")

def get_rsi(ticker, interval="minute5", period=14):
    df = pyupbit.get_ohlcv(ticker, interval=interval, count=200)
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

while True:
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=2)
        now_price = pyupbit.get_current_price(ticker)
        prev_price = df.iloc[-2]['close']
        rsi = get_rsi(ticker)

        print(f"현재가: {now_price}, RSI: {rsi:.2f}")

        if now_price < prev_price * 0.993 and rsi < 30:
            print("🟢 매수 조건 만족!")
            upbit.buy_market_order(ticker, 5000)
            log_trade("매수", now_price, 5000 / now_price)

        elif now_price > prev_price * 1.012 and rsi > 70:
            print("🔴 매도 조건 만족!")
            btc_balance = upbit.get_balance("BTC")
            if btc_balance > 0.00008:
                upbit.sell_market_order(ticker, btc_balance)
                log_trade("매도", now_price, btc_balance)

        time.sleep(30)

    except Exception as e:
        print("에러 발생:", e)
        time.sleep(10)
