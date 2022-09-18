import numpy as np
import pandas as pd
from datetime import datetime

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
        
        self.df = pd.DataFrame({'quotation': self.quotation})
        print('>>> Screener OK, number of quotes', len(self.quotation))


    def get_market_metrics(self):
        df = self.df.copy()
        
        turnover_24h = []
        open_interest = []
        funding_rate = []
        next_funding_time = []

        for row in df.itertuples():
            try:
                data = self.session.latest_information_for_symbol(
                        symbol=row.quotation)['result'][0]

                turnover_24h.append(float(data['turnover_24h']))
                open_interest.append(float(data['open_interest']))
                funding_rate.append(float(data['funding_rate']))
                date = datetime.fromisoformat(data['next_funding_time'][:-1])
                next_funding_time.append(date)
            except Exception as e:
                print(e)
        
        df['turnover_24h'] = turnover_24h
        df['open_interest'] = open_interest
        df['funding_rate'] = funding_rate
        df['next_funding_time'] = next_funding_time
        return df


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
        metrics_ = metrics.copy()
        natr = []
        for row in metrics_.itertuples():
            quotation = row.quotation
            natr.append(self.get_natr(quotation))
        
        metrics_['natr'] = natr
        return metrics_

    
    def get_screening(self, num=10):
        market_metrics = self.get_market_metrics()
        sorted_df = market_metrics.sort_values(by=['turnover_24h'], 
                                               ascending=False)
        top_10_vol = sorted_df[:num]
        return self.add_natr(top_10_vol)

    
    def get_top_natr(self, num=10):
        market_metrics = self.get_market_metrics()
        all_market_natr = self.add_natr(market_metrics)
        sorted_df = all_market_natr.sort_values(by='natr', 
                                                ascending=False)
        top_10_natr = sorted_df[:num]
        return top_10_natr

    def get_upcoming_fundings(self, num=10):
        market_metrics = self.get_market_metrics()
        upcoming_time = market_metrics['next_funding_time'].min()
        upcoming_fundings = \
            market_metrics[market_metrics['next_funding_time'] == upcoming_time]
        sorted_df = upcoming_fundings.sort_values(by=['funding_rate'], 
                                                  ascending=False)
        top_10_fund = sorted_df[:num]
        return self.add_natr(top_10_fund), upcoming_time


if __name__ == '__main__':
    screener = Screener()
    #metrics = screener.get_market_metrics()
    print(screener.get_upcoming_fundings())
    #print(screener.sorting(metrics, False, param=4))
    #top_10_vol = screener.get_top()
    #print(screener.add_natr(test_list))
    #print(screener.get_screening())