import numpy as np

from common.functions import fit_linear, fit_quadratic

if __name__ == '__main__':
    """
        From http://stackoverflow.com/a/28242456/4143531:
        C:\\Users\\Maksim\\Desktop>python tmp.py
        linear fit  [ 9.43854354 -6.18989527]
        quadratic fit [ 2.10811829 -1.06889652  4.40567418]

        C:\Python35_x64\python.exe C:/bin/mrakitin/experiments/common_run.py
        {'intercept': -6.1898951577786612, 'slope': 9.4385435302920904}
        {'c': 4.4056732765634585, 'b': -1.0688956779878316, 'a': 2.1081181533325601}
    """
    x = np.array([1.0, 2.5, 3.5, 4.0, 1.1, 1.8, 2.2, 3.7])
    y = np.array([6.008, 15.722, 27.130, 33.772, 5.257, 9.549, 11.098, 28.828])

    model_result_lin = fit_linear(x=x, y=y)
    print(model_result_lin.values)

    model_result_quad = fit_quadratic(x=x, y=y)
    print(model_result_quad.values)

    print(model_result_lin.fit_report())
    print(model_result_quad.fit_report())
