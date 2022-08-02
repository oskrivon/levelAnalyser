import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mplfinance as mpf
import numpy as np
from scipy.signal import savgol_filter
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

import df_common as dfc


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
    
    val_max.append(in_array[-1])
    val_min.append(in_array[0])

    return val_max, val_min, indexes_max, indexes_min

def touch_count(in_array, threshold, touches_count):
    touches = []
    level_prices = []
    for i in in_array:
        distance_to_level = abs(i - in_array)
        touches = np.where(distance_to_level < threshold)

    max_index = np.where(in_array == max(in_array))[0][0]

    for i in range(max_index, len(in_array)):
        distance_to_level = abs(in_array[i] - in_array)
        touches = np.where(distance_to_level < threshold)

        if len(touches[0]) >= touches_count:
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

def plot_create(x, y, y_smooth, quotation, resistance, support, 
                cluster_numbers, threshold, diff_percent):
    fig, ax = plt.subplots(figsize=(16, 8))
    plt.title(label=quotation)
    ax.grid()
    ax.plot(x, y)
    ax.plot(x, y_smooth)

    levels_resistances_txt = ""
    if len(resistance) == 0:
        levels_resistances_txt = "resistances not found"
    else:
        for i in resistance:
            ax.hlines(i, x.min(), x.max(), color = 'r', alpha = 1)
            levels_resistances_txt = levels_resistances_txt + " " + str(i.round(2))

    levels_supports_txt = ""
    if len(support) == 0:
        levels_supports_txt = "supports not found"
    else:
        for i in support:
            ax.hlines(i, x.min(), x.max(), color = 'g', alpha = 1)
            levels_supports_txt = levels_supports_txt + " " + str(i.round(2))

    tx = ("resistances: " + levels_resistances_txt + '\n' + 
          "supports: " + levels_supports_txt + '\n' + 
          "cluster count = " + str(cluster_numbers) + '\n' + 
          "threshold = " + str(threshold.round(5)) + '\n' + 
          "diff_percent = " + str(diff_percent.round(5)) + "%"
         )

    ax.text(x.min(), y.min(), tx, size = 13)

    return plt

def mpf_plot(df, quotation, resistance, support, cluster_numbers,
             threshold, diff_percent, eps):
    def levels_text_create(levels):
        tx = ''
        if len(levels) == 0:
            tx = 'resistances not found'
        else:
            for lv in levels:
                tx = tx + ' ' + str(lv.round(4))
        return tx

    resistance_tx = levels_text_create(resistance)
    support_tx = levels_text_create(support)

    tx = (quotation + '  ' + str(df.index[0]) + ' - ' + str(df.index[0]) + '\n' +
          'th = ' + str(threshold) + ' | ' + 
          'max_diff = ' + str(diff_percent.round(5)) + '%' + ' | ' + 
          'eps = ' + str(eps.round(5)) + ' | ' + 
          'cluster numbers = ' + str(cluster_numbers.round(5)) + '\n' + 
          'resistances: ' + resistance_tx + '\n' + 
          'supports: ' + support_tx
         )
    
    levels =  resistance + support
    colors = tuple(['r'] * len(resistance) + ['g'] * len(support))

    hlines_config = dict(hlines=levels, 
                         colors=colors, 
                         linewidths=1
                        )
    tittle_config = dict(title = tx, y = 1, x = 0.11,
                         fontsize = 10, fontweight = 10,
                         ha = 'left')
    save_config = dict(fname = 'images/' + quotation + '.png',
                       transparent = False)

    mpf.plot(df, type='line', volume=True, style='yahoo',
             figratio=(16,8), xrotation=0, figscale=1,
             hlines=hlines_config,
             title=tittle_config,
             savefig=save_config,
             tight_layout=True
            )

def data_preparation(quotation):
    df_path = 'market_history/' + quotation + '.csv'
    df_raw = pd.read_csv(df_path)

    # open datasets and create dataframe
    df = dfc.dataframe_create(df=df_raw,
                              drop=['symbol', 'tickDirection', 'trdMatchID', 
                                    'side', 'grossValue', 'homeNotional', 
                                     'foreignNotional'
                                     ],
                              timestamp = 's'
                              )

    # gpouping data to tameframe
    minutly_price = dfc.grouping_by_time(df)
    return minutly_price

def downhill_algorithm(t, p, val_max, val_min):
    sorted_max = np.sort(val_max)[::-1]
    sorted_min = np.sort(val_min)

    # downhill algorithm
    time = t[0]

    times_max = []
    times_min = []

    resistance_levels = []
    support_levels = []

    for val in sorted_max:
        index = np.where(val == p)[0][0]
        if t[index] > time:            
            times_max.append(t[index])
            resistance_levels.append(val)

            time = t[index]

    time = t[0]

    for val in sorted_min:
        index = np.where(val == p)[0][0]
        if t[index] > time:
            times_min.append(t[index])
            support_levels.append(val)

            time = t[index]
    
    return resistance_levels, support_levels

def DBSCAN_clusters(resistance_levels, support_levels, eps, min_samples):
    def level_clusters(levels, func):
        X = np.reshape(levels, (-1,1))
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)

        labels = db.labels_
        labels_set = set(labels)
        labels_set.discard(-1)
        clusters_num = len(labels_set)

        levels_np = np.array(levels)

        levels_array = []

        for label in labels_set:
            indexes = np.where(labels == label)
            levels_array.append(func(levels_np[indexes]))
        
        return levels_array, clusters_num

    resistance_array, clusters_resistance = level_clusters(resistance_levels, max)
    supports_array, clusters_supports = level_clusters(support_levels, min)
    clusters_num = clusters_resistance + clusters_supports

    return resistance_array, supports_array, clusters_num

def resistance_search(quotation, th, savgol_filter_param, poly, touches):
    minutly_price = data_preparation(quotation)

    # from dataframe to numpy array
    p = np.array(minutly_price['High'])
    t = np.array(minutly_price.index)

    # smoothing
    p_smooth = savgol_filter(p, savgol_filter_param, poly)

    # searching local extremes
    val_max, val_min, indexes_max, indexes_min = extremes_search(p_smooth)

    # set the threshold and percent difference
    diff_percent = (np.max(p) - np.min(p))/np.max(p)

    threshold = diff_percent * th * np.min(p_smooth)

    # level touch count for max
    level_prices = touch_count(val_max, threshold, touches)

    resistance_levels = []
    cluster_numbers = 0

    if len(level_prices) > 1:
        if len(level_prices) > 10:
            # clusters count
            cluster_numbers = silhouette_coefficient(level_prices)

            # one-cluster detection (if clusters > 2 -> cluster only one)    
            if cluster_numbers <= 3:
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
    fig = plot_create(t, p, p_smooth, quotation, resistance_levels, cluster_numbers, threshold, diff_percent)
    fig.savefig('images/' + quotation + '.png')

def resistance_search_downhill(quotation, th, savgol_filter_param, poly, touches):
    minutly_price = data_preparation(quotation)

    # from dataframe to numpy array
    p = np.array(minutly_price['High'])
    t = np.array(minutly_price.index)

    # smoothing
    p_smooth = savgol_filter(p, savgol_filter_param, poly)

    # searching local extremes
    val_max, val_min, indexes_max, indexes_min = extremes_search(p_smooth)

    # set the threshold and percent difference
    diff_percent = (np.max(p) - np.min(p))/np.max(p)

    threshold = diff_percent * th * np.min(p_smooth)

    # downhill algorithm
    resistance_levels, support_levels = downhill_algorithm(t, p_smooth, val_max, val_min, threshold)

    # gag
    cluster_numbers = 99

    fig = plot_create(t, p, p_smooth, quotation, resistance_levels, support_levels, cluster_numbers, threshold, diff_percent)
    fig.savefig('images/' + quotation + '.png')

    return resistance_levels, support_levels

def resistance_search_downhill_and_DBSCAN(quotation, th, savgol_filter_param, poly, min_samples):
    minutly_price = data_preparation(quotation)

    # from dataframe to numpy array
    p = np.array(minutly_price['High'])
    t = np.array(minutly_price.index)

    # smoothing
    p_smooth = savgol_filter(p, savgol_filter_param, poly)

    # searching local extremes
    val_max, val_min, _, _ = extremes_search(p_smooth)

    # set the threshold and percent difference
    diff_percent = (np.max(p) - np.min(p))/np.max(p)

    eps = th * (np.max(p) - np.min(p))

    # downhill algorithm
    resistance_levels, support_levels = downhill_algorithm(t, p_smooth, val_max, val_min)

    resistance_levels_db, support_levels_db, cluster_numbers = DBSCAN_clusters(resistance_levels, support_levels, eps, min_samples)

    #fig = plot_create(t, p, p_smooth, quotation, resistance_levels_db, support_levels_db, cluster_numbers, eps, diff_percent)
    #fig.savefig('images/' + quotation + '.png')

    mpf_plot(minutly_price, quotation, resistance_levels_db, support_levels_db,
             cluster_numbers, th, diff_percent, eps)

    return resistance_levels, support_levels