#!/usr/bin/python
# -*- coding: utf-8 -*-

import lmfit
import numpy as np
from matplotlib import pyplot as plt


def calc_fwhm(x, y, shift=0.5, return_as_dict=True):  # MR21062017
    """The function searches x-values (roots) where y=0 (after normalization to values between 0 and 1 and shifting the
    values down by 0.5 (default value)) based on linear interpolation, and calculates full width at half maximum (FWHM).

    :param x: an array of x values.
    :param y: an array of y values.
    :param shift: an optional shift to be used in the process of normalization (between 0 and 1).
    :param return_as_dict: if to return a dict with 'fwhm' and 'x_range'
    :return: a value of the FWHM or dictionary consisting of 'fwhm' and 'x_range'
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
        if not return_as_dict:
            return abs(list_of_roots[-1] - list_of_roots[0])
        else:
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


if __name__ == '__main__':
    # TODO: wrap it to a function and add options to the cl script.
    """
        From http://stackoverflow.com/a/28242456/4143531:
        C:\\Users\\Maksim\\Desktop>python tmp.py
        linear fit  [ 9.43854354 -6.18989527]
        quadratic fit [ 2.10811829 -1.06889652  4.40567418]

        C:\Python35_x64\python.exe C:/bin/mrakitin/experiments/common_run.py
        {'intercept': -6.1898951577786612, 'slope': 9.4385435302920904}
        {'c': 4.4056732765634585, 'b': -1.0688956779878316, 'a': 2.1081181533325601}
    """
    # x = np.array([1.0, 2.5, 3.5, 4.0, 1.1, 1.8, 2.2, 3.7])
    # y = np.array([6.008, 15.722, 27.130, 33.772, 5.257, 9.549, 11.098, 28.828])

    print_details = False

    # Elevation, 7th harmonic, 17th harmonic, 18th harmonic:
    harmonics = {
        1: '7th harmonic',
        2: '17th harmonic',
        3: '18th harmonic',
    }
    data = np.array([
        [-0.250, 0.08160, 0.03711, 0.03387],
        [-0.300, 0.07915, 0.03576, 0.03318],
        [-0.375, 0.07836, 0.03555, 0.03260],  # 7th harmonic scan #311
        [-0.450, 0.07477, 0.03595, 0.03252],
        [-0.500, 0.07688, 0.03712, 0.03313],
    ])

    x = data[:, 0]
    xx1 = np.linspace(x.min(), x.max(), 50)
    for i in sorted(harmonics.keys()):
        y = data[:, i]

        # model_result_lin = fit_linear(x=x, y=y)
        # print(model_result_lin.values)

        model_result_quad = fit_quadratic(x=x, y=y)
        print(model_result_quad.values)

        if print_details:
            # print(model_result_lin.fit_report())
            print(model_result_quad.fit_report())

        a = model_result_quad.values['a']
        b = model_result_quad.values['b']
        min_value = -b / (2 * a)
        print('Min value for {}: {}'.format(harmonics[i], min_value))

        plt.plot(x, y, 'bo')
        plt.plot(x, model_result_quad.best_fit, 'r-')
        plt.grid()
        plt.show()

        # break
