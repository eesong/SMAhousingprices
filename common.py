import numpy as np
from inspect import getsource
from re import split


def generate_min_max(mini, step):
    value = mini + np.random.randint(0, 10) * step
    return mini, mini + 10 * step, step, value


def func2str(f):
    output = getsource(f)
    output = split(r"return", output)[-1].strip()
    output = split(r"lambda: ", output)[-1].strip()[:-1]
    return output
