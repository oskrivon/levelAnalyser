import numpy as np
import datetime
import time

from pybit import usdt_perpetual
from pybit import inverse_perpetual

import level_detector as ld
import data_preparer
import plotter
import volume_analyzer as va


def preliminary_analysis(quotation, log_flag: bool, volume_flag: bool):
    th = 0.05
    df = data_preparer.data_preparation(quotation, '15m')

    high_prices = np.array(df['High'])
    low_prices = np.array(df['Low'])
    volumes = np.array(df['Volume'])
    timestamps = np.array(df.index)

    resistance_levels, support_levels = \
        ld.improvise_algorithm(high_prices, low_prices, timestamps, th)

    quantile_50, quantile_75 = \
        va.quantile_analyzer(volumes)

    if log_flag:
        plotter.mpf_plot(df, quotation, resistance_levels, support_levels,
                         th, volume_flag)

    return resistance_levels, support_levels, quantile_50, quantile_75


def volyme_analysis(session, quotation):
    interval = 15

    start_unix = datetime.datetime.now() - datetime.timedelta(hours=1)
    start = int(datetime.datetime.timestamp(start_unix))

    try:
        bybit_response = session.query_kline(
                        symbol=quotation,
                        interval=interval,
                        #limit=200,
                        from_time=start
                        )
        
        results = bybit_response['result'][:-1]
        volume = results[-1]['volume']
    except Exception as e:
        print(e)
        volume = 0
    return volume


def get_price(session, quotation):
    try:
        market_data = session.latest_information_for_symbol(symbol=quotation)
        price = float(market_data['result'][0]['last_price'])
    except Exception as e:
        print(e)
        price = 0
    return price


def market_scoring():
    session_unauth = inverse_perpetual.HTTP(
            endpoint="https://api.bybit.com"
    )

    quotations_ = session_unauth.query_symbol()

    quotation_list = []

    for i in quotations_['result']:
        quotation_list.append(i['alias'])

    session_open_value = usdt_perpetual.HTTP(
        endpoint="https://api.bybit.com"
    )

    volumes_dict = {}
    for q in quotation_list:
        volume = volyme_analysis(session_open_value, q)
        price = get_price(session_unauth, q)
        volumes_dict[q] = volume * price
        #time.sleep(0.005)
    
    print('all market data get')
    return volumes_dict