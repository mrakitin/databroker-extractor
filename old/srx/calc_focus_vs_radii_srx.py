# -*- coding: utf-8 -*-
"""The module is to perform series of the SRW simulations of the SRX beamline @ NSLS-II
with different radii of the spherical mirror to find the best radius of curvature
producing the smallest horizontal focus.

Author: Maksim Rakitin, BNL (based on O.Chubar's script).
Date: 2016-08-15
"""
import array
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import srwl_bl
import uti_io

import SRWLIB_VirtBL_SRX_01 as srx

PICS_DIR = 'pics'


def calc_series(radius_begin=5000, radius_end=20000, step=100, ap_size_x=2.5e-3, run=True, plot=True):
    radii = range(radius_begin, radius_end + 1, step)
    data = np.zeros((len(radii), 2))
    v = srwl_bl.srwl_uti_parse_options(srx.varParam)
    for i, r in enumerate(radii):
        print('\n  Value: {}\n'.format(r))
        width = get_x_width(
            v,
            mirror_radius=r,
            ap_size_x=ap_size_x,
            run=run,
            plot=plot,
        )
        data[i, 0] = r
        data[i, 1] = width

    print('Found widths ({} to {} m with step {} m):\n{}'.format(radius_begin, radius_end, step, data))
    return data


def get_x_width(v, mirror_radius=12500.0, ap_size_x=2.5e-3, run=True, plot=True):
    v.ws = True
    v.wm_fni = 'res_int_pr_me_hfm_imperf_off.dat'
    v.und_g = 6.715
    v.w_mag = 2
    v.w_e = 8000.0
    v.w_ef = 8000.0
    v.wm_ei = 0.0
    v.op_DCM_e = 8000.0
    v.w_smpf = 0.1
    v.w_rx = 2.5e-03
    v.w_ry = 2.e-03
    v.op_BL = 7
    v.op_S0_dx = ap_size_x
    v.op_S0_dy = 2.e-03

    # v.op_HFM_r = 20000.0
    v.op_HFM_r = mirror_radius

    v.op_HFM_f = 0.0
    v.op_fin = 'HFM_SMP'
    v.op_S0_pp = [0, 0, 1, 0, 0, 1.0, 3.0, 1.2, 1.0, 0, 0, 0]
    v.op_fin_pp = [0, 0, 1, 0, 0, 1.0, 1.0, 1.0, 1.0, 0, 0, 0]

    # Plotting:
    v.ws_pl = ''  # 'xy'

    # Setup optics only if Wavefront Propagation is required:
    if run:
        op = srx.set_optics(v) if (v.ws or v.wm) else None
        srwl_bl.SRWLBeamline('SRX beamline').calc_all(v, op)

    ws_file = os.path.join(v.fdir, v.ws_fni)
    skip_lines = 10
    ar2d = uti_io.read_ascii_data_cols(
        _file_path=ws_file,
        _str_sep='\t',
        _i_col_start=0,
        _i_col_end=-1,
        _n_line_skip=skip_lines,
    )[0]

    with open(ws_file, 'r') as f:
        content = f.readlines()[:skip_lines]
        x_range = [
            _parse_header(content[4], float),
            _parse_header(content[5], float),
            _parse_header(content[6], int),
        ]
        y_range = [
            _parse_header(content[7], float),
            _parse_header(content[8], float),
            _parse_header(content[9], int),
        ]

    totLen = int(x_range[2] * y_range[2])
    lenAr2d = len(ar2d)
    if lenAr2d > totLen:
        ar2d = np.array(ar2d[0:totLen])
    elif lenAr2d < totLen:
        auxAr = array.array('d', [0] * lenAr2d)
        for i in range(lenAr2d):
            auxAr[i] = ar2d[i]
        ar2d = np.array(auxAr)

    if isinstance(ar2d, (list, array)):
        ar2d = np.array(ar2d)
    ar2d = ar2d.reshape(x_range[2], y_range[2], order='F')

    x = np.linspace(x_range[0], x_range[1], x_range[2])
    y = np.linspace(y_range[0], y_range[1], y_range[2])

    x_at_zero_y = ar2d[:, y_range[2] / 2]
    max_value = x_at_zero_y.max()
    factor = 0.01
    m_to_um = 1e6
    frac_of_max = max_value * factor
    idx_ge_frac_of_max = np.where(x_at_zero_y >= frac_of_max)[0]
    x_ge_frac_of_max = x[idx_ge_frac_of_max]

    # Rescaling for plotting:
    x_um = np.copy(x) * m_to_um
    x_ge_frac_of_max_um = np.copy(x_ge_frac_of_max) * m_to_um

    vals_ge_frac_of_max = x_at_zero_y[idx_ge_frac_of_max]
    width = abs(x_ge_frac_of_max_um[-1] - x_ge_frac_of_max_um[0])  # um

    if plot:
        if not os.path.isdir(PICS_DIR):
            os.mkdir(PICS_DIR)
        units_um = u'\u00B5m'
        frac_of_max_text = '{} x max intensity'.format(factor)
        plt.figure(figsize=(10, 6))
        plt.title(
            u'Width at {} (radius={} m): {} {}'.format(frac_of_max_text, mirror_radius, round(width, 3), units_um))
        plt.xlabel(u'Horizontal Position [{}]'.format(units_um))
        plt.ylabel(u'Intensity [ph/s/.1%bw/mm²]')

        plt.plot(x_um, x_at_zero_y, label='All X values at Y=0.0')
        plt.plot(x_ge_frac_of_max_um, vals_ge_frac_of_max, c='red', label='Values >= {}'.format(frac_of_max_text))
        plt.xlim([x_ge_frac_of_max_um[0] * 2, x_ge_frac_of_max_um[-1] * 2])
        plt.grid()
        plt.axvline(0.0, c='black')
        plt.legend()
        pic_name = os.path.join(PICS_DIR, 'x_int_{:05d}.png'.format(mirror_radius))
        plt.savefig(pic_name, dpi=100)
        plt.cla()
        plt.clf()
        plt.close()

    return width


def plot_result(data, name='result.png'):
    units_um = u'\u00B5m'
    plt.figure(figsize=(10, 6))
    plt.title('Focus size vs. radius')
    plt.xlabel('Radius [m]')
    plt.ylabel(u'Focus size [{}]'.format(units_um))
    plt.plot(data[:, 0], data[:, 1])
    plt.grid()
    pic_name = os.path.join(PICS_DIR, name)
    plt.savefig(pic_name, dpi=100)
    plt.cla()
    plt.clf()
    plt.close()


def _parse_header(row, data_type):
    return data_type(row.split('#')[1].strip())


if __name__ == '__main__':
    radius_begin = 12815
    radius_end = 12825
    step = 1
    ap_size_x = 0.5e-3
    data = calc_series(
        radius_begin=radius_begin,
        radius_end=radius_end,
        step=step,
        ap_size_x=ap_size_x,
    )
    name = 'name_{}_{}_{}.png'.format(radius_begin, radius_end, step)
    plot_result(
        data=data,
        name=name,
    )
