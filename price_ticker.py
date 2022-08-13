import os
import numpy as np
import datetime

from pybit import spot
from pybit import inverse_perpetual

import level_detector as ld


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
    res, supp = ld.improvise_algorithm(quotation, 0.1, False, False)
    res_np = np.array(res)
    supp_np = np.array(supp)
    
    # get current price from market
    # https://bybit-exchange.github.io/docs/inverse/#t-latestsymbolinfo
    data = session_unauth.latest_information_for_symbol(symbol=quotation)
    current_price = float(data['result'][0]['last_price'])

    resistance_distance = abs(res_np - current_price)/current_price * 100
    support_dictance = abs(supp_np - current_price)/current_price * 100

    min_resistance_distance = np.min(resistance_distance)
    min_support_dictance = np.min(support_dictance)

    r = min_resistance_distance.round(4)
    s = min_support_dictance.round(4)

    date = datetime.datetime.utcnow()

    if min_resistance_distance <= th: 
        opening_price_long.append(current_price)
        quotations_long.append(quotation)
    if min_support_dictance <= th: 
        opening_price_short.append(current_price)
        quotation_short.append(quotation)

    #if min_resistance_distance <= th: print(i, quotation, 'long', current_price, r, s, date)
    #if min_support_dictance <= th: print(i, quotation, 'short', current_price, r, s, date)

    print(i)
    i += 1

opening_price_long_np = np.array(opening_price_long)
opening_price_short_np = np.array(opening_price_short)

while True:
    print('long:')
    print('number of quotes', len(opening_price_long_np))
    current_prices = price_checker(session_unauth, quotations_long)
    print(np.sum((current_prices - opening_price_long_np)/
           opening_price_long_np * 100))

    print('short:')
    print('number of quotes', len(opening_price_short_np))
    current_prices = price_checker(session_unauth, quotation_short)
    print(np.sum((current_prices - opening_price_short_np)/
           opening_price_short_np * 100))