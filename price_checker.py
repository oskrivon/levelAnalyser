import os
import numpy as np
import datetime

from pybit import spot
from pybit import inverse_perpetual

session_unauth = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)

dirname = 'market_history/'
files = os.listdir(dirname)

print(datetime.datetime.utcnow())
prices = []
for s in files:
    quotation = s.split('.')[0]
    data = session_unauth.latest_information_for_symbol(symbol=quotation)
    current_price = float(data['result'][0]['last_price'])
    prices.append(current_price)

print(prices)
print(datetime.datetime.utcnow())