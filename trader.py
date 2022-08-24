from sys import argv
import numpy as np
import datetime
import time
from pathlib import Path

from pybit import inverse_perpetual

import level_detector as ld
import logger as log


def str_to_bool(v):
    return str(v).lower() in ('true', '1')

quotation = str(argv[1])
volume_flag = str_to_bool(argv[2])
image_flag = str_to_bool(argv[3])

stop = 0.003
th = 0.05
dirname = 'trades/'

session_unauth = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)


def get_price():
    market_data = session_unauth.latest_information_for_symbol(symbol=quotation)
    return float(market_data['result'][0]['last_price'])


def get_current_levels():
    resists, supports = ld.improvise_algorithm(quotation, 0.1, volume_flag, image_flag)
    if len(resists) > 0:
        resistance_level = np.array(resists)[-1]
    else:
        resistance_level = 0
    
    if len(supports) > 0:
        support_level = np.array(supports)[-1]
    else:
        support_level = 0

    return resistance_level, support_level


def open_log():
    date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H-%M')
    path = dirname + quotation + ' ' + date + '.txt'
    file = Path(path)
    file.touch(exist_ok=True)
    return open(file, 'w')


def open_trade(side, current_price):
    log_file = open_log()

    date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    buy_price = current_price

    if side == 'long':
        stop_loss = buy_price - buy_price * stop
    if side == 'short':
        stop_loss = buy_price + buy_price * stop

    log_msg = log.log_open_trade(date, side, buy_price, stop_loss)
    log_file.write(log_msg + '\n')

    return date, buy_price, stop_loss, log_file


def close_trade(current_price, log_file):
    date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    sell_price = current_price
    profit = (sell_price - buy_price) / buy_price * 100

    log_msg = log.log_close_trade(date, sell_price, profit)

    log_file.write(log_msg + '\n')
    log_file.close()

    #return date, sell_price, profit


def trade(side, stop_loss, buy_price, order, log_file):
    while order:
        current_price = get_price()

        if side == 'long':
            if current_price <= stop_loss:
                order = False
                close_trade(current_price, log_file)

            if current_price > buy_price:
                stop_loss = current_price - current_price * (stop / 3)
        else:
            if current_price >= stop_loss:
                order = False
                close_trade(current_price, log_file)

            if current_price < buy_price:
                stop_loss = current_price + current_price * (stop / 3)


calc_time = time.perf_counter()
resistance_level, support_level = get_current_levels()

while True:
    current_price = get_price()

    if resistance_level != 0:
        resistance_distance = abs(resistance_level - current_price) / current_price * 100
        if resistance_distance <= th:
            side = 'long'
            date, buy_price, stop_loss, log_file = open_trade(side, current_price)

            order = True
            trade(side, stop_loss, buy_price, order, log_file)

    if support_level != 0:
        support_distance = abs(support_level - current_price) / current_price * 100    
        if support_distance <= th:
            side = 'short'
            date, buy_price, stop_loss, log_file = open_trade(side, current_price)

            order = True
            trade(side, stop_loss, buy_price, order, log_file)
    
    if (current_price > resistance_level) or (current_price < support_level):
        resistance_level, support_level = get_current_levels()

    if (resistance_level == 0) or (support_level == 0):
        new_calc_time = time.perf_counter()
        if new_calc_time - calc_time >= 5 * 60:
            resistance_level, support_level = get_current_levels()
            calc_time = time.perf_counter()