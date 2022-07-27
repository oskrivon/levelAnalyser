import datetime
import pandas as pd
from pybit import inverse_perpetual
from urllib.error import HTTPError


def get_market_history(quotations = [], period = 3):
    # get the now data
    now = datetime.datetime.now()
    print(now.year, now.month, now.day)

    if len(quotations) == 0:
        # get the quotations from bybit
        session_unauth = inverse_perpetual.HTTP(
            endpoint="https://api-testnet.bybit.com"
        )
        quotations_ = session_unauth.query_symbol()

        quotation_list = []

        for i in quotations_['result']:
            quotation_list.append(i['alias'])
    else:
        quotation_list = []

        for i in quotations:
            quotation_list.append(i)

    quotation_list.sort()

    # create the urls list
    url_list = []

    for i in quotation_list:
        urls = []
        for j in range(period, 0, -1):
            url = ('https://public.bybit.com/trading/' + i + '/' + i + str(now.year) + '-0' + 
            str(now.month) + '-' + str(now.day - j) + '.csv.gz'
            )
            urls.append(url)
        url_list.append(urls)

    # market data download
    for i in url_list:
        df = []
        for j in i:
            try:
                df_ = pd.read_csv(j)
            except HTTPError:
                continue

            df.append(df_)

        try:
            df_total = pd.concat(df)
            df_total.reset_index(drop=True, inplace=True)

            s = i[0].split('/')
            file_name = s[4]

            df_total.to_csv('market_history/' + file_name + '.csv')
        except ValueError:
                continue