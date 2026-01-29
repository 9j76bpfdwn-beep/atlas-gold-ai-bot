worker: python main.py
import os
import time
import requests
import pandas as pd
import pandas_ta as ta
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
API_KEY = os.getenv("TWELVEDATA_API_KEY", "")

API_URL = "https://api.twelvedata.com/time_series"
RISK_PERCENT = 1
