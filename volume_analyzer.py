import numpy as np


def volume_analyzer(volumes: np.array, timestamp: np.array):
    mean = np.mean(volumes)
    last = volumes[-1]
    print(np.mean(volumes))

    return mean, last