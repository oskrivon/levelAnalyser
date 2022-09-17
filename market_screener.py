import numpy as np

import talib
from pybit import inverse_perpetual

import data_preparer

test_list = \
    [['BTCUSD', 10943347813600.0, 451577968, '2022-09-17T16:00:00Z'], 
    ['ETHUSD', 449309338887.8, 226872792, '2022-09-17T16:00:00Z'], 
    ['BTCUSDT', 3008518839.85, 48759.57, '2022-09-17T16:00:00Z'], 
    ['ETHUSDT', 2501056220.6879997, 341516.89, '2022-09-17T16:00:00Z'], 
    ['ATOMUSDT', 263943453.675, 2127719.2, '2022-09-17T16:00:00Z'], 
    ['LUNA2USDT', 217587574.774, 4068263, '2022-09-17T16:00:00Z'], 
    ['ETCUSDT', 177998703.021, 976940.6, '2022-09-17T16:00:00Z'], 
    ['LTCUSD', 126658627.55, 5729037, '2022-09-17T16:00:00Z'], 
    ['1000LUNCUSDT', 124985615.55559999, 39915343, '2022-09-17T16:00:00Z'],
    ['SOLUSD', 123247447.18, 2714407, '2022-09-17T16:00:00Z']]

class Screener:
    def __init__(self):
        self.session = inverse_perpetual.HTTP(
                endpoint="https://api.bybit.com"
                )


    def get_top_10(self):
        quotations_ = self.session.query_symbol()

        quotation_list = []
        market_slice = []

        for i in quotations_['result']:
            quotation_list.append(i['alias'])

        counter = 0
        for i in quotation_list:
            try:
                data = self.session.latest_information_for_symbol(symbol=i)['result'][0]
                quote_scoring = [data['symbol'], 
                                 float(data['turnover_24h']), 
                                 float(data['open_interest']), 
                                 data['next_funding_time']]
                market_slice.append(quote_scoring)
                #counter += 1
                #if counter >= 20: break
            except Exception as e:
                print(e)
                
        sorted_slice = (sorted(market_slice, 
            key=lambda market_slice: market_slice[1],
            reverse=True))
        top_10_volumes = sorted_slice#[:10]

        return top_10_volumes


    def add_natr(self, metrics):
        for metric in metrics:
            df = data_preparer.data_preparation(metric[0], '15m')

            x = 100
            timeperiod = 14
            
            high = np.array(df['High'])[-x:]
            low = np.array(df['Low'])[-x:]
            close = np.array(df['Close'])[-x:]

            natr = talib.NATR(high, low, close, timeperiod)
            metric.append(natr[-1])
        
        return metrics

    
    def get_screening(self):
        top_10_vol = self.get_top_10()
        return self.add_natr(top_10_vol)


if __name__ == '__main__':
    screener = Screener()
    #top_10_vol = screener.get_top_10()
    print(screener.add_natr(test_list))
    #print(screener.get_screening())