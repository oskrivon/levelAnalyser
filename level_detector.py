import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import df_common as dfc


def extremes_search(in_array):
    val_max, val_min, indexes_max, indexes_min = [], [], [], []
    for i in range(1, len(in_array)-1):
        if in_array[i] >= in_array[i-1]:
            if in_array[i] >= in_array[i+1]:
                val_max.append(in_array[i])
                indexes_max.append(i)

    if in_array[-1] > in_array[-2]:
        val_max.append(in_array[-1])
    if in_array[0] > in_array[1]:
        val_max.append(in_array[0])

    for i in range(0, len(in_array)-1):
        if in_array[i] <= in_array[i-1]:
            if in_array[i] <= in_array[i+1]:
                val_min.append(in_array[i])
                indexes_min.append(i)
    
    if in_array[-1] < in_array[-2]:
        val_min.append(in_array[-1])
    if in_array[0] < in_array[1]:
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


def downhill_algorithm(t, p, val_max, val_min):
    last_time = t[-1] - np.timedelta64(20, 'm')

    def level_screening(sorted_levels):
        levels = []
        time = t[0]

        for val in sorted_levels:
            index = np.where(val == p)[0][-1]
            if t[index] >= time:
                if t[index] < last_time:            
                    levels.append(val)
                    time = t[index]
        
        return levels
    
    sorted_max = np.sort(val_max)[::-1]
    sorted_min = np.sort(val_min)

    resistance_levels = level_screening(sorted_max)
    support_levels = level_screening(sorted_min)
    
    return resistance_levels, support_levels


def improvise_algorithm(price: np.array, timestamp: np.array, th):
    # from dataframe to numpy array
    p = price
    t = timestamp

    # searching local extremes
    val_max, val_min, _, _ = extremes_search(p)

    # downhill algorithm
    resistance_levels, support_levels = downhill_algorithm(t, p, val_max, val_min)

    # set the threshold and percent difference
    eps = th * (np.max(p) - np.min(p))

    # search in maximums
    level_touches_res = []
    resistance_levels = sorted(resistance_levels, reverse=True)

    for level in resistance_levels:
        if len(level_touches_res) == 0:
            index = np.where(level == p)[0][-1]
            highest = len(np.where(p[index:] > level)[0])

            if highest == 0:
                level_touches_res.append(level)
        else:
            diff = level_touches_res[-1] - level
            if diff >= eps:
                index = np.where(level == p)[0][-1]
                highest = len(np.where(p[index:] > level)[0])

                if highest == 0:
                    level_touches_res.append(level)

    for level in level_touches_res:
        count = 0
        for level_ in resistance_levels:
            diff = abs(level - level_)
            if diff <= eps: count +=1

    # search in minimums
    level_touches_sup = []
    support_levels = sorted(support_levels)

    for level in support_levels:
        if len(level_touches_sup) == 0:
            index = np.where(level == p)[0][-1]
            highest = len(np.where(p[index:] < level)[0])

            if highest == 0:
                level_touches_sup.append(level)
        else:
            diff = level - level_touches_sup[-1]
            if diff >= eps:
                index = np.where(level == p)[0][-1]
                highest = len(np.where(p[index:] < level)[0])

                if highest == 0:
                    level_touches_sup.append(level)

    for level in level_touches_sup:
        count = 0
        for level_ in support_levels:
            diff = abs(level - level_)
            if diff <= eps: count +=1

    return level_touches_res, level_touches_sup