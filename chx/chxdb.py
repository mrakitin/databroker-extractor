# -*- coding: utf-8 -*-
"""
This is a library for experimental data processing from the CHX beamline of NSLS-II. It requires the SRW utils library,
please download https://github.com/ochubar/SRW/blob/master/env/work/srw_python/uti_math.py#L615 and add it to your
PYTHONPATH environment variable.
"""

import chxtools.xfuncs as xf  # from https://github.com/NSLS-II-CHX/chxtools/blob/master/chxtools/xfuncs.py
import databroker as db  # get_fields, get_images, get_table
import numpy as np
from matplotlib import pyplot as plt

import common.databroker as c_db
import common.math as c_math


def get_and_plot(scan_id, save=False, field='', intensity_field='elm_sum_all', idx=None, is_vs_energy=False):
    """Get data from table and plot it (produces Intensity vs. Ugap or mono angle).

    :param scan_id: scan id from bluesky.
    :param save: an option to save a picture instead of showing it.
    :param field: visualize the intensity vs. this field.
    :param idx: index of the image (used as a part of the name in the saving process).
    :return: None.
    """
    g, e, t = get_data(scan_id, field=field, intensity_field=intensity_field)
    if is_vs_energy:
        g = xf.get_EBragg('Si111cryo', np.abs(g)) * 1e3  # keV -> eV
    plot_scan(g, e, scan_id=scan_id, timestamp=t, save=save, field=field, idx=idx, is_vs_energy=is_vs_energy)


def get_data(scan_id, field='ivu_gap', intensity_field='elm_sum_all', det=None, debug=False):
    """Get data from the scan stored in the table.

    :param scan_id: scan id from bluesky.
    :param field: visualize the intensity vs. this field.
    :param intensity_field: the name of the intensity field.
    :param det: the name of the detector.
    :param debug: a debug flag.
    :return: a tuple of X, Y and timestamp values.
    """
    scan, t = c_db.get_scan(scan_id)
    if det:
        imgs = db.get_images(scan, det)
        im = imgs[-1]
        if debug:
            print(im)

    table = db.get_table(scan)
    fields = db.get_fields(scan)

    if debug:
        print(table)
        print(fields)
    x = table[field]
    y = table[intensity_field]

    return x, y, t


def plot_scan(x, y, scan_id, timestamp, save, field, idx, is_vs_energy):
    """Plot intensities vs. scan variable.

    :param x: scan variable.
    :param y: intensity.
    :param scan_id: scan id from bluesky.
    :param timestamp: a timestamp of the scan.
    :param save: a flag to save the produced image.
    :param field: visualize the intensity vs. this field.
    :param idx: index of the image (used as a part of the name in the saving process).
    :return: None.
    """
    x = np.array(x)
    y = np.array(y)
    if field == 'ivu_gap':
        units = 'mm'
    elif field == 'dcm_b':
        units = 'deg'
    else:
        raise ValueError('Unknown field: {}'.format(field))

    if is_vs_energy:
        field = 'energy'
        units = 'eV'

    try:
        fwhm_value = c_math.calc_fwhm(x, y)['fwhm']
    except Exception:
        fwhm_value = -1

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111)
    ax.scatter(x, y)
    ax.grid()
    ax.set_title('Scan ID: {}    Timestamp: {}\nFWHM: {:.5f} {}'.format(scan_id, timestamp, fwhm_value, units))
    xlabel = field.replace('_', ' ')

    ax.set_xlabel('{} [{}]'.format(xlabel, units))
    ax.set_ylabel('Intensity [arb. units]')
    if not save:
        plt.show()
    else:
        if idx is not None:
            plt.savefig('scan_{:02d}_{}.png'.format(idx, scan_id))
        else:
            plt.savefig('scan_{}.png'.format(scan_id))
