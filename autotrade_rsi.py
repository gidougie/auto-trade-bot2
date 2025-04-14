import pyupbit
import time
import pandas as pd
from datetime import datetime

# ✅ 너의 업비트 API 키 입력
access = "fmQ6nYgxfsHb7rBE48Os8cOsIMd60SDV5DrgVJGY"
secret = "CJbtsyKmW0hmRvcbCHEpiunncbUHcom2XWF4JWfd"
upbit = pyupbit.Upbit(access, secret)

ticker = "KRW-BTC"

def log_trade(action, price, volume):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{action}] {price}원 | 수량: {volume:.6f} | 시간: {now}")
    df = pd.DataFrame([[now, action, price, volume]], columns=["시간", "구분", "가격", "수량"])
    df.to_csv("trading_log.csv", mode='a', header=False, index=False)

def get_rsi(ticker, interval="minute1", period=14):
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
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2)
        now_price = pyupbit.get_current_price(ticker)
        prev_price = df.iloc[-2]['close']
        rsi = get_rsi(ticker)

        print(f"[LOG] 현재가: {now_price}, 이전가: {prev_price}, RSI: {rsi:.2f}")
        print(f"[BOT] 실행 중... ({datetime.now().strftime('%H:%M:%S')})")  # ✅ 서버 유지용 로그

        # 🟢 공격적 매수 조건
        if now_price < prev_price * 0.997 and rsi < 50:
            print("🟢 공격적 매수 조건 만족!")
            upbit.buy_market_order(ticker, 50000)
            log_trade("매수", now_price, 50000 / now_price)

        # 🔴 공격적 매도 조건
        elif now_price > prev_price * 1.006 and rsi > 55:
            print("🔴 공격적 매도 조건 만족!")
            btc_balance = upbit.get_balance("BTC")
            if btc_balance > 0.00008:
                upbit.sell_market_order(ticker, btc_balance)
                log_trade("매도", now_price, btc_balance)

        time.sleep(30)

    except Exception as e:
        print(f"🚨 에러 발생: {e}")
        time.sleep(10)
