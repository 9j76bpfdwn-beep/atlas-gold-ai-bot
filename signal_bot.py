import os
import requests
from statistics import mean

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

SYMBOL = "XAUUSD"
INTERVAL = "15min"
LIMIT = 200

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload, timeout=15)

def ema(values, period):
    k = 2 / (period + 1)
    out = [values[0]]
    for price in values[1:]:
        out.append(price * k + out[-1] * (1 - k))
    return out

def rsi(values, period=14):
    gains, losses = [], []
    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))
    avg_gain = mean(gains[-period:])
    avg_loss = mean(losses[-period:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Fetch candles
resp = requests.get(
    "https://api.twelvedata.com/time_series",
    params={"symbol": SYMBOL, "interval": INTERVAL, "outputsize": LIMIT, "apikey": TWELVEDATA_API_KEY},
    timeout=20
).json()

if "values" not in resp:
    raise Exception(f"TwelveData error: {resp}")

closes = [float(v["close"]) for v in reversed(resp["values"])]

# Indicators
price = closes[-1]
ema20 = ema(closes, 20)[-1]
ema50 = ema(closes, 50)[-1]
ema200 = ema(closes, 200)[-1]
rsi_val = rsi(closes)

# SHORT-only logic
short_ok = (price < ema200) and (ema20 < ema50) and (rsi_val < 50)

if short_ok:
    sl = round(max(closes[-10:]), 2)
    tp = round(price - (sl - price) * 1.8, 2)

    msg = (
        f"📉 *XAUUSD SHORT SIGNAL*\n\n"
        f"Entry: `{round(price,2)}`\n"
        f"Stop Loss: `{sl}`\n"
        f"Take Profit: `{tp}`\n\n"
        f"TF: 15m | RSI: `{round(rsi_val,1)}`\n"
        f"Reason: price<EMA200, EMA20<EMA50, RSI<50\n\n"
        f"⚠️ Risk management required"
    )
    send_telegram(msg)
