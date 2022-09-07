import numpy as np

import level_detector as ld
import data_preparer
import plotter
import volume_analyzer as va


def preliminary_analysis(quotation, log_flag: bool, volume_flag: bool):
    th = 0.05
    df = data_preparer.data_preparation(quotation, '15m')

    high_prices = np.array(df['High'])
    low_prices = np.array(df['Low'])
    volumes = np.array(df['Volume'])
    timestamps = np.array(df.index)

    resistance_levels, support_levels = \
        ld.improvise_algorithm(high_prices, low_prices, timestamps, th)

    quantile_50, quantile_75 = \
        va.quantile_analyzer(volumes)

    if log_flag:
        plotter.mpf_plot(df, quotation, resistance_levels, support_levels,
                         th, volume_flag)

    return resistance_levels, support_levels, quantile_50, quantile_75