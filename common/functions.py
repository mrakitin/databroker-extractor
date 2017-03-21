import lmfit
import numpy as np
from matplotlib import pyplot as plt


def calc_fwhm(x, y):  # MR27092016
    """The function searches x-values (roots) where y=0 based on linear interpolation, and calculates FWHM"""

    def is_positive(num):
        return True if num > 0 else False

    positive = is_positive(y[0])
    list_of_roots = []
    for i in range(len(y)):
        current_positive = is_positive(y[i])
        if current_positive != positive:
            list_of_roots.append(x[i - 1] + (x[i] - x[i - 1]) / (abs(y[i]) + abs(y[i - 1])) * abs(y[i - 1]))
            positive = not positive
    if len(list_of_roots) >= 2:
        return abs(list_of_roots[-1] - list_of_roots[0])
    else:
        raise Exception('Number of roots is less than 2!')


def clear_plt():
    """Clear the plots (useful when plotting in a loop).

    :return: None
    """
    plt.cla()
    plt.clf()
    plt.close()


def fit_quadratic():
    # TODO: implement quadratic fitting using lmfit library.
    m = lmfit.models.QuadraticModel()
    pass


def normalize(y, shift=0.5):
    return (y - np.min(y)) / (np.max(y) - np.min(y)) - shift  # roots are at Y=0
