from turtle import shape
import numpy as np
import pandas as pd


def volume_analyzer(volumes: np.array):
    previous = volumes[-2]

    d = {'volumes': volumes}
    data = pd.DataFrame(data=d)

    q50 = data.quantile(q=.50)[0]

    return previous, q50