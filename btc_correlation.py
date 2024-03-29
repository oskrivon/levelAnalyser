import os
import pandas as pd
import numpy as np

import df_common as dfc

df_raw = pd.read_csv('market_history/BTCUSDT.csv')


df_raw = dfc.dataframe_create(df=df_raw,
                            drop=['symbol', 'tickDirection', 'trdMatchID', 
                                'side', 'grossValue', 'homeNotional', 
                                    'foreignNotional'
                                    ],
                            timestamp = 's'
                            )

minutly_price = dfc.grouping_by_time(df_raw)

begin = str(minutly_price.index[100])
end = str(minutly_price.index[-100])

def get_np_from_df(quotation):
    path = 'market_history/'
    df_raw = pd.read_csv(path + quotation + '.csv')

    df_raw = dfc.dataframe_create(df=df_raw,
                              drop=['symbol', 'tickDirection', 'trdMatchID', 
                                    'side', 'grossValue', 'homeNotional', 
                                     'foreignNotional'
                                     ],
                              timestamp = 's'
                              )

    minutly_price = dfc.grouping_by_time(df_raw)

    new_prices = minutly_price[(minutly_price.index > begin) &
                               (minutly_price.index < end)]
    
    return np.array(new_prices['High'])

btc = get_np_from_df('BTCUSDT')

def correlation_to_file():
    dirname = 'market_history/'
    files = os.listdir(dirname)

    correlation_file = open('correlation.txt', 'w')
    correlation_array = np.array([])

    for file in files:
        quotation = file.split('.')[0]

        print(file)
        coin = get_np_from_df(quotation)
        try:
            correlation = np.corrcoef(btc, coin)[0,1]
            correlation_file.write(quotation + ':' + str(correlation) + '\n')
            correlation_array = np.append(correlation_array, correlation)
        except ValueError:        
            correlation_file.write(quotation + ':' + 'ValueError' + str(len(btc)) + ' vs ' + str(len(coin)) + '\n')

    correlation_file.close()

def corellation_quotation(quotation):
    coin = get_np_from_df(quotation)

    try:
        correlation = np.corrcoef(btc, coin)[0,1]
        #correlation_array = np.append(correlation_array, correlation)
        return correlation
    except ValueError:
        return 1