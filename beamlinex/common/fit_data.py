#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
An example of linear and quadratic fit from http://stackoverflow.com/a/28242456/4143531.
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import leastsq

import beamlinex.common.command_line as cl
import beamlinex.common.plot as c_plot


def fit_data(beamline, study='elevation', no_save=True):
    allowed_beamlines = ('chx', 'CHX', 'smi', 'SMI')
    assert beamline in allowed_beamlines, '{}: incorrect beamline.  Allowed values: {}'.format(study, allowed_beamlines)

    # data provided
    # x=np.array([1.0,2.5,3.5,4.0,1.1,1.8,2.2,3.7])
    # y=np.array([6.008,15.722,27.130,33.772,5.257,9.549,11.098,28.828])

    if beamline.lower() == 'smi':
        allowed_values = ('elevation', 'taper')
        assert study in allowed_values, '{}: incorrect study name.  Allowed values: {}'.format(study, allowed_values)

        harmonics = {
            1: '7th harmonic',
            # 2: '17th harmonic',
            # 3: '18th harmonic',
        }

        if study == 'elevation':
            # Elevation parameters:
            x_units = 'mm'
            x_label = 'Elevation [{}]'.format(x_units)
            y_label = 'FWHM [deg]'
            data = np.array([
                [-0.200, 0.07161],  # scan_id = 565
                [-0.150, 0.07109],  # scan_id = 566
                [-0.100, 0.06995],  # scan_id = 567
                [-0.050, 0.06963],  # scan_id = 569
                [0.000, 0.06924],  # scan_id = 570
                [0.050, 0.06981],  # scan_id = 571
                [0.100, 0.06944],  # scan_id = 572
                [0.150, 0.06904],  # scan_id = 573
                [0.200, 0.06964],  # scan_id = 574
            ])
        elif study == 'taper':
            # Taper parameters:
            x_units = 'µm'
            x_label = 'Taper [{}]'.format(x_units)
            y_label = 'FWHM [deg]'
            data = np.array([
                [18.2, 0.09091, 0.04181, 0.03983],
                [8.5, 0.08191, 0.03745, 0.03437],
                [0.14, 0.07738, 0.03570, 0.03258],
                [-4.8, 0.07652, 0.03510, 0.03274],
                [-10, 0.07636, 0.03621, 0.03369],
                [-15, 0.07547, 0.03700, 0.03501],
                [-22, 0.07720, 0.03715, 0.03800],
            ])
        else:
            raise ValueError('Unknown study name: {}'.format(study))

    elif beamline.lower() == 'chx':
        allowed_values = ('elevation')
        assert study in allowed_values, '{}: incorrect study name.  Allowed values: {}'.format(study, allowed_values)

        harmonics = {
            1: '7th harmonic',
            2: '11th harmonic',
        }

        if study == 'elevation':
            # Elevation parameters:
            x_units = 'mm'
            x_label = 'Elevation [{}]'.format(x_units)
            y_label = 'FWHM [deg]'
            data = np.array([
                [0.150, 0.06885, 0.04420],
                [0.100, 0.06303, 0.03978],
                [0.050, 0.05874, 0.03663],
                [0.0005, 0.05851, 0.03588],
                [-0.0085, 0.05742, 0.03560],
                [-0.050, 0.05826, 0.03708],
                [-0.100, 0.06067, 0.03840],
                [-0.150, 0.06654, 0.04276],
            ])
        else:
            raise ValueError('Unknown study name: {}'.format(study))

    x = data[:, 0]
    for i in sorted(harmonics.keys()):
        y = data[:, i]

        # here, create lambda functions for Line, Quadratic fit
        # tpl is a tuple that contains the parameters of the fit
        funcLine = lambda tpl, x: tpl[0] * x + tpl[1]
        funcQuad = lambda tpl, x: tpl[0] * x ** 2 + tpl[1] * x + tpl[2]

        # func is going to be a placeholder for funcLine,funcQuad or whatever
        # function we would like to fit
        func = funcLine

        # ErrorFunc is the diference between the func and the y "experimental" data
        ErrorFunc = lambda tpl, x, y: func(tpl, x) - y

        # tplInitial contains the "first guess" of the parameters
        tplInitial1 = (1.0, 2.0)

        # leastsq finds the set of parameters in the tuple tpl that minimizes
        # ErrorFunc=yfit-yExperimental
        tplFinal1, success = leastsq(ErrorFunc, tplInitial1[:], args=(x, y))
        # print('Linear fit: {}'.format(tplFinal1))

        xx1 = np.linspace(x.min() - np.abs(x.min()) * 0.05, x.max() + np.abs(x.max()) * 0.05, 100)
        yy1 = func(tplFinal1, xx1)

        # ------------------------------------------------
        # now the quadratic fit
        # -------------------------------------------------
        func = funcQuad
        tplInitial2 = (1.0, 2.0, 3.0)

        tplFinal2, success = leastsq(ErrorFunc, tplInitial2[:], args=(x, y))
        print('Quadratic fit: {}'.format(tplFinal2))
        xx2 = xx1

        a = tplFinal2[0]
        b = tplFinal2[1]
        min_value = -b / (2 * a)
        print('Min value for {}: {}\n'.format(harmonics[i], min_value))

        yy2 = func(tplFinal2, xx2)

        # Identify y_min and y_max:
        y_min = np.min([y.min(), yy2.min()])
        y_min -= np.abs(y_min) * 0.01

        y_max = np.max([y.max(), yy2.max()])
        y_max += np.abs(y_max) * 0.01

        # Plotting procedure:
        plt.title('{}'.format(harmonics[i]))
        # plt.plot(xx1, yy1, 'g-', label='linear fit')
        plt.scatter(x, y, label='measurements')
        plt.plot(xx2, yy2, 'r-', label='quadratic fit (min={:.3f} {})'.format(min_value, x_units))
        plt.axvline(min_value, color='black')
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        plt.ylim((y_min, y_max))
        plt.legend()
        plt.grid()
        plt.tight_layout()
        if not no_save:
            plt.savefig('{}_fit_{}.png'.format(study, harmonics[i]))
        else:
            plt.show()
        c_plot.clear_plt()


if __name__ == "__main__":
    args = cl.parse_studies()
    fit_data(beamline=args.beamline, study=args.study, no_save=args.no_save)
