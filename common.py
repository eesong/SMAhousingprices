import numpy as np


def generate_min_max(mini, step):
    value = mini + np.random.randint(0, 10) * step
    return mini, mini + 10 * step, step, value
