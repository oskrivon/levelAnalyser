from turtle import shape
import numpy as np
import pandas as pd


def quantile_analyzer(volumes: np.array):
    d = {'volumes': volumes}
    data = pd.DataFrame(data=d)

    q50 = data.quantile(q=.50)[0]
    q75 = data.quantile(q=.75)[0]

    return q50.item(), q75.item()