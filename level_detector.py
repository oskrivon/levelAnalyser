import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


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

def extremes_search(in_array):
    val_max, val_min, indexes_max, indexes_min = [], [], [], []
    for i in range(1, len(in_array)-1):
        if in_array[i] > in_array[i-1]:
            if in_array[i] > in_array[i+1]:
                val_max.append(in_array[i])
                indexes_max.append(i)

    for i in range(0, len(in_array)-1):
        if in_array[i] < in_array[i-1]:
            if in_array[i] < in_array[i+1]:
                val_min.append(in_array[i])
                indexes_min.append(i)
    return val_max, val_min, indexes_max, indexes_min

def touch_count(in_array, threshold):
    touches = []
    level_prices = []
    for i in in_array:
        distance_to_level = abs(i - in_array)
        touches = np.where(distance_to_level < threshold)

    max_index = np.where(in_array == max(in_array))[0][0]

    for i in range(max_index, len(in_array)):
        distance_to_level = abs(in_array[i] - in_array)
        touches = np.where(distance_to_level < threshold)

        if len(touches[0]) >= 5:
            #index = np.where(p_smooth == in_array[i])[0]
            #plt.hlines(val_max[i], t[index], t.max(), color = 'b', alpha = 0.2)
            #levels.append([len(touches[0]), in_array[i]])
            level_prices.append(in_array[i])
    return level_prices

def silhouette_coefficient(data):
    data_reshape = np.reshape(data, (-1, 1))

    scores = []
    coefficient = []
    
    for k in range(2,4):
        estimator = KMeans (n_clusters = k)
        estimator.fit(data_reshape)
        try:
            scores.append(silhouette_score(data_reshape,estimator.labels_,metric='euclidean'))
        except ValueError:
            scores.append(0)
        coefficient.append(k)
    
    index_of_max = scores.index(max(scores))
    return coefficient[index_of_max]

def plot_create(x, y, quotation, levels, cluster_numbers, threshold, diff_percent):
  fig, ax = plt.subplots(figsize=(16, 8))
  plt.title(label=quotation)
  ax.grid()
  ax.plot(x, y)

  levels_txt = ""
  if len(levels) == 0:
    levels_txt = "levels not found"
  else:
    for i in levels:
      ax.hlines(i, x.min(), x.max(), color = 'r', alpha = 0.5)
      levels_txt = levels_txt + " " + str(i.round(2))

  tx = ("level = " + levels_txt + '\n' + 
        "cluster count = " + str(cluster_numbers) + '\n' + 
        "threshold = " + str(threshold.round(5)) + '\n' + 
        "diff_percent = " + str(diff_percent.round(5)) + "%"
    )

  ax.text(x.min(), y.min(), tx, size = 13)

  return fig

def resistance_search(quotation):
    savgol_filter_param = 50

    df_path = 'market_history/' + quotation + '.csv'
    df_raw = pd.read_csv(df_path)

    # open datasets and create dataframe
    df = dataframe_create(df=df_raw,
                            drop=['symbol', 'tickDirection', 'trdMatchID', 
                                'side', 'grossValue', 'homeNotional', 
                                'foreignNotional'
                                ],
                            timestamp = 's'
                            )

    # gpouping data to tameframe
    minutly_price = grouping_by_time(df)

    new_prices = minutly_price[1000:-1000]

    # from dataframe to numpy array
    p = np.array(new_prices['High'])
    t = np.array(new_prices.index)

    # smoothing
    p_smooth = savgol_filter(p, savgol_filter_param, 3)

    # searching local extremes
    val_max, val_min, indexes_max, indexes_min = extremes_search(p_smooth)

    # set the threshold and percent difference
    th = 0.1
    diff_percent = (np.max(p) - np.min(p))/np.max(p)

    threshold = diff_percent * th * np.min(p_smooth)

    # level touch count for max
    level_prices = touch_count(val_max, threshold)

    resistance_levels = []
    cluster_numbers = 0

    if len(level_prices) > 1:
        if len(level_prices) > 10:
            # clusters count
            cluster_numbers = silhouette_coefficient(level_prices)

            # one-cluster detection (if clusters > 2 -> cluster only one)    
            if cluster_numbers <= 2:
                level_prices_reshape = np.reshape(level_prices, (-1, 1))

                kmeans = KMeans(n_clusters = cluster_numbers)
                kmeans.fit(level_prices_reshape)

                labels = kmeans.labels_
                for i in range(cluster_numbers):
                    indexes = np.where(labels == i)[0]
                    max_index = np.min(indexes)

                    resistance_levels.append(level_prices[max_index])
            else:
                resistance_levels.append(max(level_prices))
        else:
            resistance_levels.append(max(level_prices))

    # plot create
    return plot_create(t, p, quotation, resistance_levels, cluster_numbers, threshold, diff_percent)

