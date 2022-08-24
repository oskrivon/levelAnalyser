from sys import argv
import numpy as np
import datetime
from pathlib import Path

from pybit import inverse_perpetual


quotation = str(argv[1])
side = str(argv[2])

stop = 0.003
dirname = 'trades/'

side_ = ''
buy_price = 0
sell_price = 0
profit = 0
stop_loss = 0

session_unauth = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)

market_data = session_unauth.latest_information_for_symbol(symbol=quotation)
current_price = float(market_data['result'][0]['last_price'])
buy_price = current_price

date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H-%M')

path = dirname + quotation + ' ' + date + '.txt'

file = Path(path)
file.touch(exist_ok=True)
f = open(file, 'w')

if side == 'long': 
    side_ = side
    stop_loss = buy_price - buy_price * stop

    open_trade = (str(date) + '\n' + 
                  side_ + '\n' + 
                  'buy price: ' + str(buy_price) + '\n' + 
                  'stop loss ' + str(stop_loss) + '\n')

    f.write(open_trade + '\n')

    order = True

    while order:
        market_data = session_unauth.latest_information_for_symbol(symbol=quotation)
        current_price = float(market_data['result'][0]['last_price'])
        profit = (current_price - buy_price) / buy_price * 100

        if current_price <= stop_loss:
                order = False
                date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                sell_price = current_price
                profit = (sell_price - buy_price) / buy_price * 100

                close_trade = (str(date) + '\n' + 
                               'sell price: ' + str(sell_price) + '\n' + 
                               'profit: ' + str(profit))
                f.write(close_trade + '\n')
            
        if current_price > buy_price:
            stop_loss = current_price - current_price * (stop / 3)


if side == 'short':
    side_ = side
    stop_loss = buy_price + buy_price * stop

    open_trade = (str(date) + '\n' + 
                  side_ + '\n' + 
                  'buy price: ' + str(buy_price) + '\n' + 
                  'stop loss' + str(stop_loss) + '\n')

    f.write(open_trade + '\n')

    order = True

    while order:
        market_data = session_unauth.latest_information_for_symbol(symbol=quotation)
        current_price = float(market_data['result'][0]['last_price'])
        profit = (buy_price - current_price) / buy_price * 100

        if current_price >= stop_loss:
            order = False
            date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            sell_price = current_price
            profit = (buy_price - current_price) / buy_price * 100

            close_trade = (str(date) + '\n' + 
                           'sell price: ' + str(sell_price) + '\n' + 
                           'profit: ' + str(profit))
            f.write(close_trade + '\n')

        if current_price < buy_price:
            stop_loss = current_price + current_price * (stop / 3)

f.close()