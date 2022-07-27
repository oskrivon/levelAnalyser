import pandas as pd

def dataframe_create(df, **kwargs):
    for i in kwargs.items():
        if i[0] == 'drop':
            df_total = df.drop(i[1], axis=1)
        elif i[0] == 'timestamp':
            df_total['timestamp'] = pd.to_datetime(df_total['timestamp'], unit=i[1])
    return df_total

def grouping_by_time(df, frequency = 'min', round = 5):
    grouped_price = df.groupby([pd.Grouper(
    key='timestamp', freq=frequency)]).agg(
        Open = ('price', 'first'),
        High = ('price', 'max'),
        Low = ('price', 'min'),
        Close = ('price', 'last'),
        Volume = ('size', 'sum'), ).round(round)

    # clearing nan-values
    grouped_price = grouped_price.fillna(method="ffill")
    grouped_price = grouped_price.fillna(method="bfill")
    return grouped_price