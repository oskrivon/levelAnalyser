from sys import argv
import numpy as np
import pandas as pd
import datetime
import time
from pathlib import Path

from pybit import inverse_perpetual
from pybit import usdt_perpetual

import level_detector as ld
import logger
import analyzer


def str_to_bool(v):
    return str(v).lower() in ('true', '1')

quotation = str(argv[1])
volume_flag = str_to_bool(argv[2])
image_flag = str_to_bool(argv[3])

#quotation = 'ETHUSDT'
#volume_flag = False
#image_flag = False

stop = 0.003
th = 0.05
dirname = 'trades/'
lof_dirname = 'trades/logs/'


log = logger.Logger(quotation)


session_unauth = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
    )

session_open_value = usdt_perpetual.HTTP(
    endpoint="https://api.bybit.com"
    )


def get_makret_data():
    market_data = session_unauth.latest_information_for_symbol(symbol=quotation)
    price = float(market_data['result'][0]['last_price'])
    open_interest = float(market_data['result'][0]['open_interest'])

    return price, open_interest

def get_price():
    market_data = session_unauth.latest_information_for_symbol(symbol=quotation)
    return float(market_data['result'][0]['last_price'])


# return levels AND QUANTILE!
def get_current_levels():
    resists, supports, quantile_50, quantile_75 = analyzer.preliminary_analysis(quotation, image_flag, volume_flag)

    if len(resists) > 0:
        resistance_level = np.array(resists)[-1]
    else:
        resistance_level = 0
    
    if len(supports) > 0:
        support_level = np.array(supports)[-1]
    else:
        support_level = 0

    return resistance_level, support_level, quantile_50, quantile_75


def open_trade(side, current_price, quantile_50, quantile_75):
    log.create()

    buy_price = current_price

    
    # sketch of the volume-module
    interval = 15

    start_unix = datetime.datetime.now() - datetime.timedelta(hours=1)
    start = int(datetime.datetime.timestamp(start_unix))

    bybit_response = session_open_value.query_kline(
                    symbol=quotation,
                    interval=interval,
                    #limit=200,
                    from_time=start
                    )
    
    results = bybit_response['result'][:-1]
    volume = results[-1]['volume']
    # sketch end

    # sketch for open interest
    period = '5min'
    bybit_response = session_unauth.open_interest(
                     symbol=quotation,
                     period=period
                     )

    open_interest = bybit_response['result'][0]['open_interest']
    # sketch end

    if side == 'long':
        stop_loss = buy_price - buy_price * stop
    if side == 'short':
        stop_loss = buy_price + buy_price * stop

    info = {
        'opening time': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'side': side,
        'buy price': buy_price,
        'stop loss': stop_loss,
        'quantile 50': quantile_50,
        'quantile 75': quantile_75,
        'volume': volume,
        'open interest': open_interest
    }
    print(info)
    log.update(**info)

    return buy_price, stop_loss


def close_trade(current_price):
    sell_price = current_price
    profit = (sell_price - buy_price) / buy_price * 100

    info = {
        'closing time': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'sell price': sell_price,
        'profit': profit
    }
    log.update(**info)

    #return date, sell_price, profit


def trade(side, stop_loss, buy_price, order):
    timestamp = []
    prices = []

    date_open = datetime.datetime.utcnow().strftime('%Y-%m-%d %H-%M')

    while order:
        current_price = get_price()

        if side == 'long':
            timestamp.append(datetime.datetime.utcnow())
            prices.append(current_price)

            if current_price <= stop_loss:
                order = False

                log_list = {'timestamp': timestamp, 'price': prices}
                df = pd.DataFrame(log_list)
                df.to_csv(lof_dirname + quotation + ' ' + date_open + '.csv')

                close_trade(current_price)

            if current_price > buy_price:
                stop_loss = current_price - current_price * (stop / 3)
        else:
            timestamp.append(datetime.datetime.utcnow())
            prices.append(current_price)

            if current_price >= stop_loss:
                order = False

                log_list = {'timestamp': timestamp, 'price': prices}
                df = pd.DataFrame(log_list)
                df.to_csv(lof_dirname + quotation + ' ' + date_open + '.csv')

                close_trade(current_price)

            if current_price < buy_price:
                stop_loss = current_price + current_price * (stop / 3)


calc_time = time.perf_counter()
resistance_level, support_level, quantile_50, quantile_75 = get_current_levels()

while True:
    current_price = get_price()

    if resistance_level != 0:
        resistance_distance = abs(resistance_level - current_price) / current_price * 100

        if resistance_distance <= th:
            side = 'long'
            buy_price, stop_loss = open_trade(side, current_price, quantile_50, quantile_75)

            order = True
            trade(side, stop_loss, buy_price, order)

    if support_level != 0:
        support_distance = abs(support_level - current_price) / current_price * 100
        
        if support_distance <= th:
            side = 'short'
            buy_price, stop_loss = open_trade(side, current_price, quantile_50, quantile_75)

            order = True
            trade(side, stop_loss, buy_price, order)
    
    if (current_price > resistance_level) or (current_price < support_level):
        resistance_level, support_level, quantile_50, quantile_75 = get_current_levels()

    if (resistance_level == 0) or (support_level == 0):
        new_calc_time = time.perf_counter()
        if new_calc_time - calc_time >= 5 * 60:
            resistance_level, support_level, quantile_50, quantile_75 = get_current_levels()
            calc_time = time.perf_counter()