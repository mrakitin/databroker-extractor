import argparse
import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.spatial.distance as spd

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
    x_calc += shift

    # Map the calculated data to the experimental mesh:
    y_calc_exp_mesh = np.interp(x_exp, x_calc, y_calc)

    # Measure similarity:
    cosine = spd.cosine(y_calc_exp_mesh, y_exp)

    return cosine, y_calc_exp_mesh


def plot_data(exp_file, calc_file, x_exp, y_exp, y_calc_exp_mesh, cosine, precision=6,
              x_label='Photon Energy [eV]', y_label='Intensity, arb. units', show=False):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111)
    base_calc_file = os.path.basename(calc_file)
    base_exp_file = os.path.basename(exp_file)

    save_fig_file = '{}_{}.png'.format(os.path.splitext(base_exp_file)[0].split('-')[0],
                                       os.path.splitext(base_calc_file)[0])

    ax.plot(x_exp, y_calc_exp_mesh,
            label='Calculated data: {} (norm. and interp. to exp.data)'.format(base_calc_file))
    ax.plot(x_exp, y_exp, label='Experimental data: {}'.format(base_exp_file))

    ax.set_title('Cosine distance: {0:.{1}f}'.format(cosine, precision))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.grid()
    ax.legend()

    plt.savefig(save_fig_file)
    if show:
        plt.show()

    clear_plt()

    return save_fig_file


def read_exp(exp_file, conversion_factor=1):
    """Read experimental data.

    :param exp_file: experimental CSV file from databroker.
    :param conversion_factor: the factor to make common units (e.g., keV -> eV)
    :return: x and y values.
    """
    exp_data = pd.read_csv(exp_file)
    x_exp = exp_data[x_label]
    y_exp = exp_data[y_label]
    x_exp *= conversion_factor
    return x_exp, y_exp


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
    return x_calc, y_calc


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

    # Read data from the both sources:
    x_exp, y_exp = read_exp(exp_file=exp_file, conversion_factor=1000)  # convert keV -> eV
    ens = []
    cos = []
    for calc_file in calc_files:
        x_calc, y_calc = read_calc(calc_file=calc_file)

        # Calculate cosine distance:
        cosine, y_calc_exp_mesh = calc_dist(x_calc=x_calc, y_calc=y_calc,
                                            x_exp=x_exp, y_exp=y_exp)

        # Plot:
        save_fig_file = plot_data(exp_file=exp_file, calc_file=calc_file, x_exp=x_exp, y_exp=y_exp,
                                  y_calc_exp_mesh=y_calc_exp_mesh, cosine=cosine)

        ens.append(float(os.path.basename(calc_file).split('_')[4]))
        cos.append(cosine)

        print('File: {}    Cosine distance: {:.6f}'.format(save_fig_file, cosine))

    plt.plot(ens, cos)
    plt.grid()
    plt.title('Min cosine distance: {:.6f} for energy spread: {}'.format(np.min(cos), ens[np.argmin(cos)]))
    plt.xlabel('Energy spread, 1e-3')
    plt.ylabel('Cosine distance')
    plt.savefig('cosine_vs_ens.png')
    plt.show()
