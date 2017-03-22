import lmfit
import numpy as np


def calc_fwhm(x, y, shift=0.5):  # MR21032017
    """The function searches x-values (roots) where y=0 (after normalization to values between 0 and 1 and shifting the
    values down by 0.5 (default value)) based on linear interpolation, and calculates full width at half maximum (FWHM).

    :param x: an array of x values.
    :param y: an array of y values.
    :param shift: an optional shift to be used in the process of normalization (between 0 and 1).
    :return: a dictionary consisting of 'fwhm' and 'x_range'
    """

    def is_positive(num):
        return True if num > 0 else False

    # Normalize values first:
    y = (y - np.min(y)) / (np.max(y) - np.min(y)) - shift  # roots are at Y=0

    positive = is_positive(y[0])
    list_of_roots = []
    for i in range(len(y)):
        current_positive = is_positive(y[i])
        if current_positive != positive:
            list_of_roots.append(x[i - 1] + (x[i] - x[i - 1]) / (abs(y[i]) + abs(y[i - 1])) * abs(y[i - 1]))
            positive = not positive
    if len(list_of_roots) >= 2:
        return {
            'fwhm': abs(list_of_roots[-1] - list_of_roots[0]),
            'x_range': list_of_roots,
        }
    else:
        raise Exception('Number of roots is less than 2!')


def fit_linear(x, y):
    """See https://lmfit.github.io/lmfit-py/model.html."""
    m = lmfit.models.LinearModel()
    params = m.make_params(a=1, b=2)
    model_result = m.fit(data=y, params=params, x=x)
    return model_result


def fit_quadratic(x, y):
    """See https://lmfit.github.io/lmfit-py/model.html."""
    m = lmfit.models.QuadraticModel()
    params = m.make_params(a=1, b=2, c=3)
    model_result = m.fit(data=y, params=params, x=x)
    return model_result
