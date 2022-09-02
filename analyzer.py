from sys import argv
import numpy as np

from pybit import inverse_perpetual

import level_detector as ld
import data_preparer
import plotter
import volume_analyzer as va


def preliminary_analysis(quotation, log_flag: bool, volume_flag: bool):
    th = 0.05
    df = data_preparer.data_preparation(quotation, '15m')

    prices = np.array(df['High'])
    volumes = np.array(df['Volume'])
    timestamps = np.array(df.index)

    resistance_levels, support_levels = ld.improvise_algorithm(prices, timestamps, th)
    quantile_50, quantile_75 = va.quantile_analyzer(volumes)

    if log_flag:
        plotter.mpf_plot(df, quotation, resistance_levels, support_levels,
                         th, volume_flag)

    return resistance_levels, support_levels, quantile_50, quantile_75