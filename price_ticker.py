import os
import numpy as np
import datetime
import time

from pybit import spot
from pybit import inverse_perpetual

import level_detector as ld
import telegram_posting as bot

TOKEN = open('telegram_key.txt', 'r').read()


def price_checker(session, quotations):
    prices_ = []
    for q in quotations:
        data_ = session.latest_information_for_symbol(symbol=q)
        current_price_ = float(data_['result'][0]['last_price'])
        prices_.append(current_price_)
    return np.array(prices_)


session_unauth = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)

th = 0.05

dirname = 'market_history/'
files = os.listdir(dirname)

quotations_long = []
opening_price_long = []

quotation_short = []
opening_price_short = []

i = 0
for s in files:
    side = ''

    quotation = s.split('.')[0]

    # get current levels from analyser
    res, supp = ld.improvise_algorithm(quotation, 0.1, False, True)
    res_np = np.array(res)
    supp_np = np.array(supp)
    
    # get current price from market
    # https://bybit-exchange.github.io/docs/inverse/#t-latestsymbolinfo
    data = session_unauth.latest_information_for_symbol(symbol=quotation)
    current_price = float(data['result'][0]['last_price'])

    min_resistance_distance = abs(res_np[-1] - current_price) / current_price * 100
    min_support_dictance = abs(supp_np[0] - current_price) / current_price * 100

    print(min_resistance_distance, min_support_dictance)

    stop = 0.001

    if (min_resistance_distance < min_support_dictance) and (min_resistance_distance < th):
        side = 'long'
        buy_price = current_price
        sell_price = 0
        profit = 0

        date = datetime.datetime.utcnow()
        stop_loss = buy_price - buy_price * stop

        #bot.telegram_message_send(str(date), TOKEN)

        msg = str(date) + '\n' + quotation + ' ' + side + ' buy: ' + str(buy_price) + ', stop loss: ' + str(round(stop_loss, 4))

        bot.telegram_message_send(msg, TOKEN)

        order = True

        while order:
            data = session_unauth.latest_information_for_symbol(symbol=quotation)
            current_price = float(data['result'][0]['last_price'])

            profit = (current_price - buy_price) / buy_price * 100
            
            if current_price <= stop_loss:
                order = False
                date = datetime.datetime.utcnow()
                sell_price = current_price
            
            if current_price > buy_price:
                stop_loss = current_price - current_price * stop
            
            print(quotation, 'current:', current_price, '(', round(profit, 3), ')',
                  'stop:', round(stop_loss, 4))
        
        #bot.telegram_message_send(str(date), TOKEN)

        profit = (sell_price - buy_price) / buy_price * 100

        msg = str(date) + '\n' + 'sell price: ' + str(sell_price) + ' profit: ' + str(round(profit, 4))
        bot.telegram_message_send(msg, TOKEN)

    print(i)
    i += 1

    if (min_support_dictance < min_resistance_distance) and (min_support_dictance < th):
        side = 'short'
        buy_price = current_price
        sell_price = 0
        profit = 0

        date = datetime.datetime.utcnow()
        stop_loss = buy_price + buy_price * stop

        #bot.telegram_message_send(str(date), TOKEN)

        msg = str(date) + '\n' + quotation + ' ' + side + ' sell: ' + str(buy_price) + ', stop loss: ' + str(round(stop_loss, 4))

        bot.telegram_message_send(msg, TOKEN)

        order = True

        while order:
            data = session_unauth.latest_information_for_symbol(symbol=quotation)
            current_price = float(data['result'][0]['last_price'])

            profit = (buy_price - current_price) / buy_price * 100
            
            if current_price >= stop_loss:
                order = False
                date = datetime.datetime.utcnow()
                sell_price = current_price
            
            if current_price < buy_price:
                stop_loss = current_price + current_price * stop
            
            print(quotation, 'current:', current_price, '(', round(profit, 3), ')',
                  'stop:', round(stop_loss, 4))
        
        #bot.telegram_message_send(str(date), TOKEN)

        profit = (buy_price - sell_price) / buy_price * 100
        
        msg = str(date) + '\n' + 'sell price: ' + str(sell_price) + ' profit: ' + str(round(profit, 4))
        bot.telegram_message_send(msg, TOKEN)

    print(i)
    i += 1