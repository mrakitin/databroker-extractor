import argparse
import glob
import os

import chxtools.xfuncs as xf  # from https://github.com/NSLS-II-CHX/chxtools/blob/master/chxtools/xfuncs.py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.spatial.distance as spd

from databroker_extractor.common.io import save_data_pandas
from databroker_extractor.common.math import calc_fwhm
from databroker_extractor.common.plot import clear_plt


def calc_dist(x_calc, y_calc, x_exp, y_exp):
    """Calculate cosine distance between experimental and calculated datasets.

    :param x_calc: calculated X values.
    :param y_calc: calculated Y values.
    :param x_exp: experimental X values.
    :param y_exp: experimental Y values.
    :return: cosine distance and interpolated calculated Y values on the experimental X mesh.
    """
    # Normalize calculated data on maximum of experimental data:
    y_calc *= y_exp.max() / y_calc.max()

    # Calculate shift of the data and shift the calculated data:
    shift = x_exp[y_exp.argmax()] - x_calc[y_calc.argmax()]  # eV

    cosines = []
    meshes = []
    shifts = []
    for pct in np.linspace(-10, 10, 10001):
        new_shift = shift * (1. + pct / 100.)
        new_x_calc = x_calc + new_shift

        # Map the calculated data to the experimental mesh:
        y_calc_exp_mesh = np.interp(x_exp, new_x_calc, y_calc)

        # Measure similarity:
        cosine = spd.cosine(y_calc_exp_mesh, y_exp)

        cosines.append(cosine)
        meshes.append(y_calc_exp_mesh)
        shifts.append(new_shift)

    # Find min cosine and the corresponding mesh:
    idx = np.argmin(cosines)

    return cosines[idx], meshes[idx], shifts[idx]


def plot_data(exp_file, calc_file, x_exp, y_exp, y_calc_exp_mesh, cosine, precision=6, shift=None,
              x_label='Photon Energy [eV]', y_label='Intensity, arb. units', show=False):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111)
    base_calc_file = os.path.basename(calc_file)
    base_exp_file = os.path.basename(exp_file)

    save_fig_file = '{}_{}.png'.format(os.path.splitext(base_exp_file)[0].split('-')[0],
                                       os.path.splitext(base_calc_file)[0])

    ax.plot(x_exp, y_calc_exp_mesh,
            label='Calculated data: {} (norm. and interp. to exp.data)'.format(base_calc_file))
    ax.scatter(x_exp, y_exp, s=10, c='red', label='Experimental data: {}'.format(base_exp_file))

    ax.set_title('Cosine distance: {0:.{1}f}  offset: {2:.3f} eV'.format(cosine, precision, shift))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.grid()
    ax.legend()

    plt.savefig(save_fig_file)
    if show:
        plt.show()

    clear_plt()

    return save_fig_file


def read_exp(exp_file, conversion_factor=1, convert_to_energy=False, material='Si111cryo', d_spacing=None):
    """Read experimental data.

    :param exp_file: experimental CSV file from databroker.
    :param conversion_factor: the factor to make common units (e.g., keV -> eV)
    :return: x and y values.
    """
    exp_data = pd.read_csv(exp_file)
    x_exp = exp_data[x_label]
    if convert_to_energy:
        x_exp = xf.get_EBragg(material, theta_Bragg=np.abs(x_exp), d_spacing=d_spacing) * 1e3  # keV -> eV
    y_exp = exp_data[y_label]
    x_exp *= conversion_factor
    fwhm_exp = _calc_fwhm(x_exp, y_exp)
    return x_exp, y_exp, fwhm_exp


def read_calc(calc_file, header_rows=10):
    """Read calculated data

    :param calc_file: the *.dat file from a SRW simulation.
    :param header_rows: number of informational rows in header of the file.
    :return: x and y values.
    """
    with open(calc_file) as f:
        content = f.readlines()
    header = content[:header_rows]
    eph_init = _parse_header(header[1], data_type=float)
    eph_fin = _parse_header(header[2], data_type=float)
    n_points = _parse_header(header[3], data_type=int)
    x_calc = np.linspace(eph_init, eph_fin, n_points)
    y_calc = np.loadtxt(calc_file, skiprows=header_rows)
    assert n_points == len(y_calc), \
        'Number of points {} does not match the length of the read data {}'.format(len(y_calc), n_points)
    fwhm_exp = _calc_fwhm(x_calc, y_calc)
    return x_calc, y_calc, fwhm_exp


def _calc_fwhm(x, y):
    try:
        fwhm = calc_fwhm(x, y)['fwhm']
    except:
        fwhm = -1
    return fwhm


def _parse_header(header_row, data_type):
    """Parse the header of a SRW data file.

    :param header_row: header row.
    :param data_type: data type.
    :return: parsed value.
    """
    return data_type(header_row.split('#')[1].strip())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Distance measure between experimental and calculated data sets')
    parser.add_argument('-c', '--calc-file', dest='calc_file', default=None,
                        help='calculated data file (*.dat from SRW)')
    parser.add_argument('-d', '--calc-dir', dest='calc_dir', default=None,
                        help='dir with the calculated data files (*.dat from SRW)')
    parser.add_argument('-e', '--exp-file', dest='exp_file', default=None,
                        help='experimental data file (*.csv from databroker)')
    parser.add_argument('-x', '--x-label', dest='x_label', default='energy_energy', help='x label to plot')
    parser.add_argument('-y', '--y-label', dest='y_label', default='bpmAD_stats3_total', help='y label to plot')
    parser.add_argument('-t', '--convert-to-energy', dest='convert_to_energy', action='store_true',
                        help='convert to energy from Bragg diffraction angle')
    parser.add_argument('--d-spacing', dest='d_spacing', default=None,
                        help='an arbitrary d-spacing of the crystal of the DCM [A]')
    args = parser.parse_args()

    if (not args.exp_file) or (not args.calc_file and not args.calc_dir):
        parser.print_help()
        parser.exit()

    calc_files = []
    if args.calc_file:
        calc_files = [args.calc_file]
    elif args.calc_dir:
        calc_files = sorted(glob.glob(os.path.join(args.calc_dir, 'res_*.dat')))
    else:
        raise ValueError('No calc files specified')

    exp_file = args.exp_file
    x_label = args.x_label
    y_label = args.y_label
    convert_to_energy = args.convert_to_energy
    d_spacing = args.d_spacing
    if d_spacing:
        d_spacing = float(d_spacing)

    # Read data from the both sources:
    if not convert_to_energy:
        kwargs = {
            'exp_file': exp_file,
            'conversion_factor': 1000,
        }
    else:
        kwargs = {
            'exp_file': exp_file,
            'conversion_factor': 1,
            'convert_to_energy': True,
            'd_spacing': d_spacing,  # convert Bragg angle -> eV
        }
    x_exp, y_exp, fwhm_exp = read_exp(**kwargs)  # convert keV -> eV

    ens = []
    cos = []
    for calc_file in calc_files:
        x_calc, y_calc, fwhm_calc = read_calc(calc_file=calc_file)

        # Calculate cosine distance:
        cosine, y_calc_exp_mesh, shift = calc_dist(x_calc=x_calc, y_calc=y_calc,
                                                   x_exp=x_exp, y_exp=y_exp)
        print('FWHM exp: {:.5f} eV    FWHM calc: {:.5f} eV'.format(fwhm_exp, fwhm_calc))

        # Plot:
        save_fig_file = plot_data(exp_file=exp_file, calc_file=calc_file, x_exp=x_exp, y_exp=y_exp,
                                  y_calc_exp_mesh=y_calc_exp_mesh, cosine=cosine, shift=shift)

        # Save data:
        columns = ['energy', 'intensity_calc', 'intensity_exp']
        data = pd.DataFrame(np.array([x_exp, y_calc_exp_mesh, y_exp]).T, columns=columns)
        fname = os.path.splitext(save_fig_file)[0]
        file_name_dat = '{}.dat'.format(fname)
        file_name_csv = '{}.csv'.format(fname)
        save_data_pandas(file_name_dat, data, columns, index=True, justify='right')
        data.to_csv(file_name_csv)

        try:
            ens_value = float(os.path.basename(calc_file).split('_')[4])
        except:
            ens_value = -1.
        ens.append(ens_value)
        cos.append(cosine)

        print('File: {}    Cosine distance: {:.6f}'.format(save_fig_file, cosine))

    plt.plot(ens, cos)
    plt.grid()
    plt.title('Min cosine distance: {:.6f} for energy spread: {}'.format(np.min(cos), ens[np.argmin(cos)]))
    plt.xlabel('Energy spread, 1e-3')
    plt.ylabel('Cosine distance')
    plt.savefig('cosine_vs_ens.png')
    plt.show()
