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

        # get all quotes from bybit
        self.quotation = []
        result = self.session.query_symbol()['result']
        for r in result:
            name = r['name']
            if name[-1] == 'T': self.quotation.append(r['name'])
        print('>>> Screener OK, number of quotes', len(self.quotation))

    def sorting(self, in_list, param=1):
        sorted_list = (sorted(in_list, 
            key=lambda market_slice: market_slice[param],
            reverse=True))
        return sorted_list


    def get_martet_metrics(self):
        market_slice = []
        for i in self.quotation:
            try:
                data = self.session.latest_information_for_symbol(symbol=i)['result'][0]
                quote_scoring = [data['symbol'], 
                                 float(data['turnover_24h']), 
                                 float(data['open_interest']), 
                                 data['funding_rate']]
                market_slice.append(quote_scoring)
            except Exception as e:
                print(e)
        return market_slice


    def get_natr(self, quotation):
        df = data_preparer.data_preparation(quotation, '15m')

        x = 100 # magick number, if < natr be worst
        timeperiod = 14
        
        high = np.array(df['High'])[-x:]
        low = np.array(df['Low'])[-x:]
        close = np.array(df['Close'])[-x:]

        natr = talib.NATR(high, low, close, timeperiod)[-1]

        return natr


    def add_natr(self, metrics):
        for metric in metrics:
            quotation = metric[0]
            metric.append(self.get_natr(quotation))        
        return metrics
    

    def natr_all_market(self):
        natr_list = []
        for q in self.quotation:
            natr_list.append(self.get_natr(q))
        return natr_list

    
    def get_screening(self, num=10):
        market_metrics = self.get_martet_metrics()
        # param=1 - is volumes
        top_10_vol = self.sorting(market_metrics, param=1)[:num]
        return self.add_natr(top_10_vol)

    
    def get_top_natr(self, num=10):
        market_metrics = self.get_martet_metrics()
        all_market_natr = self.add_natr(market_metrics)
        top_10_natr = self.sorting(all_market_natr, param=4)[:num]
        return top_10_natr


if __name__ == '__main__':
    screener = Screener()
    print(screener.quotation)
    #top_10_vol = screener.get_top()
    #print(screener.add_natr(test_list))
    #print(screener.get_screening())