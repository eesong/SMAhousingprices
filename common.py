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


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)


# a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# print(running_mean(a, 5))
