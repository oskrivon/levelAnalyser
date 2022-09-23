import requests
import pandas as pd
import json
from datetime import datetime
from pprint import pprint


import conn_binance_stream as stream


class BinanceConnector:
    def __init__(self):
        self.endpoint = 'https://fapi.binance.com/'


    # getting all quotes from binance. 
    # First get all USDT quotes, then all missing BUSD's
    def get_all_quotes(self):
        r = requests.get(self.endpoint + 'fapi/v1/exchangeInfo')
        print(r)
        r_json = json.loads(r.text)
        symbols = r_json['symbols']
        quotes_USDT = [x['baseAsset'] for x in symbols if 'USDT' in x['quoteAsset']]
        quotes_BUSD = [x['baseAsset'] for x in symbols if 'BUSD' in x['quoteAsset'] and 
                       x['baseAsset'] not in quotes_USDT]

        quotes_all = [x + 'USDT' for x in quotes_USDT] + \
                     [x + 'BUSD' for x in quotes_BUSD]
        return quotes_all


    def get_fundings(self, df_inn):
        df_quotes = df_inn.copy()
        print(df_quotes)
        quotes = df_quotes['quotation'].to_list()
        quotes_, funding_rate, funding_time = \
            stream.get_last_fundings(quotes)

        df = pd.DataFrame({
            'quotation': quotes_,
            'funding_rate': funding_rate,
            'next_funding_time': funding_time
        })
        print(df)
        return df


    def get_server_time(self):
        r = requests.get(self.endpoint + 'fapi/v1/time')
        server_time = json.loads(r.text)['serverTime']
        return server_time

    
    def get_klines(self):
        r = requests.get(self.endpoint + 'fapi/v1/klines')
        pass


if __name__ == '__main__':
    connector = BinanceConnector()
    quotation = connector.get_all_quotes()
    df = pd.DataFrame({'quotation': quotation})
    print(connector.get_fundings(df))

'''''''''
    payload = {
        'symbol': 'BTCUSDT',
        'interval': '15m',
        'limit': 99
    }
    r = requests.get(
        'https://fapi.binance.com/fapi/v1/klines',
        params=payload
        )

    bybit_server = 'https://fapi.binance.com/fapi/v1/klines'
    path = 'market_history/binance/'

    bybit_server = 'https://fapi.binance.com/fapi/v1/ticker/24hr'

    bybit_server = 'https://fapi.binance.com/fapi/v1/fundingRate'
    quotation = 'BTCUSDT'

    while True:
        payload = {
            'symbol': 'BTCUSDT',
            'limit': 10
        }

        r = requests.get(bybit_server, params=payload)
        ticker_24h = json.loads(r.text)
        for f in ticker_24h:
            print(f['fundingRate'])
            print(datetime.utcfromtimestamp(int(f['fundingTime'])/1000).strftime('%Y-%m-%d %H:%M:%S'))

    while True:
        payload = {
            'symbol': 'BTCUSDT'
        }

        r = requests.get(bybit_server, params=payload)
        ticker_24h = json.loads(r.text)
        print(ticker_24h['quoteVolume'])

    for quotation in symbols_all:
        payload = {
            'symbol': quotation,
            'interval': '15m',
            'limit': 99
        }

        r = requests.get(bybit_server, params=payload)

        klines_raw = json.loads(r.text)
        columns = [
            'Open time', 'Open', 'High', 'Low', 'Close',
            'Volume', 'Close time', 'Quote asset volume',
            'Number of trades', 'Taker buy base asset volume',
            'Taker buy quote asset volume', 'Ignore'
            ]
        df_klines = pd.DataFrame(klines_raw, columns=columns)
        df = df_klines[[
            'Open time', 'Open', 'High', 'Low', 
            'Close', 'Volume'
            ]]
        df.to_csv(path + quotation + '.csv')
        status_code = r.status_code
        print(status_code)
        if status_code != 200: 
            print(status_code)
            break
      '''''''''''  