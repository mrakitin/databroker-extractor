import datetime
import time

import numpy as np
from databroker import db, get_fields, get_table
from matplotlib import pyplot as plt
from uti_math import fwhm as calc_fwhm


def fit_quadratic():
    # TODO: implement quadratic fitting using lmfit library.
    pass


def normalize(y, shift=0.5):
    return (y - np.min(y)) / (np.max(y) - np.min(y)) - shift  # roots are at Y=0


def plot_scans(scan_ids, offset_hours=-5, norm=None, x_label='bragg', y_label='VFMcamroi1', show=True):
    timestamp = datetime.datetime.fromtimestamp(time.time() + offset_hours * 3600).strftime('%Y-%m-%d_%H_%M_%S')
    d = read_scans(scan_ids)
    y_max = np.array(d['y_list']).max()

    _clear_plt()

    for i in range(len(scan_ids)):
        x = d['x_list'][i]
        y = d['y_list'][i]
        if norm == 'total':
            y = y / y_max
        elif norm == 'individual':
            y = y / np.array(d['y_list'][i]).max()
        plt.plot(x, y, label='scan_id={},\nFWHM={:.5f}'.format(d['real_scan_ids'][i], d['fwhm_values'][i]))

    plt.legend()

    plt.title(
        'UID:{}\nscan_id: {}'.format(
            d['uids'][-1],
            ', '.join([str(x) for x in d['real_scan_ids']]),
        )
    )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()

    plt.savefig('timestamp_{}_scan_{}.png'.format(timestamp, d['real_scan_ids'][-1]))

    if show:
        plt.show()


def read_scans(scan_ids, x_label='bragg', y_label='VFMcamroi1'):
    real_scan_ids = []
    uids = []
    x_list = []
    y_list = []
    fwhm_values = []
    for scan_id in scan_ids:
        d = read_single_scan(scan_id, x_label=x_label, y_label=y_label)
        real_scan_ids.append(d['scan_id'])
        uids.append(d['uid'])
        x_list.append(d['x'])
        y_list.append(d['y'])
        fwhm_values.append(d['fwhm'])

    return {
        'real_scan_ids': real_scan_ids,
        'uids': uids,
        'x_list': x_list,
        'y_list': y_list,
        'fwhm_values': fwhm_values,
    }


def read_single_scan(scan_id, x_label='bragg', y_label='VFMcamroi1'):
    scan = db[scan_id]
    fields = get_fields(scan)
    data = get_table(scan)
    x = np.array(data[x_label])
    y = np.array(data[y_label])
    try:
        fwhm = calc_fwhm(x, normalize(y))
    except:
        fwhm = -1

    return {
        'scan': scan,
        'scan_id': scan.start.scan_id,
        'uid': scan.start.uid,
        'fields': fields,
        'data': data,
        'x': x,
        'y': y,
        'x_label': x_label,
        'y_label': y_label,
        'fwhm': fwhm,
    }


def save_data(scan_id, columns_from_plots=False, index=False):
    """Save data to a file.

    :param scan_id: scan id to save data for.
    :param columns_from_plots: save columns from plots (all columns are saved by default).
    :param index: if print the index column.
    :return file_name: name of the saved file.
    """
    d = read_single_scan(scan_id)
    file_name = 'scan_{}.dat'.format(d['scan_id'])
    columns = [d['x_label'], d['y_label']] if columns_from_plots else None
    with open(file_name, 'w') as f:
        f.write(d['data'].to_string(columns=columns, index=index, justify='left'))
    return file_name


def _clear_plt():
    """Clear the plots (useful when plotting in a loop).

    :return: None
    """
    plt.cla()
    plt.clf()
    plt.close()


def _parse_scan_ids(scans_list):
    try:
        scan_ids = [int(x) for x in scans_list]
    except:
        raise ValueError('Incorrect scan ids provided: {}'.format(scans_list))
    if not scan_ids:
        scan_ids = [-1]
    return scan_ids


if __name__ == '__main__':
    import argparse

    # Plot a single graph:
    parser = argparse.ArgumentParser(description='Visualize data for NSLS-II SMI beamline')
    # Plot data:
    parser.add_argument('-p', '--plot-ids', dest='plot_ids', default=None, nargs='*',
                        help='plot data for blank-separated scan ids list')
    parser.add_argument('-n', '--norm-plots', dest='norm_plots', default=None, choices=('total', 'individual'),
                        help='normalize plots')
    # Save data:
    parser.add_argument('-s', '--save-ids', dest='save_ids', default=None, nargs='*',
                        help='save data for blank-separated scan ids list')
    parser.add_argument('-c', '--columns-from-plots', dest='columns_from_plots', action='store_true',
                        help='save columns from plots')
    parser.add_argument('-x', '--hide-index-column', dest='hide_index_column', action='store_false',
                        help='hide index column in the saved file(s)')

    args = parser.parse_args()

    if args.plot_ids is None and args.save_ids is None:
        parser.print_help()
        parser.exit()

    if args.plot_ids is not None:
        scan_ids = _parse_scan_ids(args.plot_ids)
        plot_scans(scan_ids=scan_ids, norm=args.norm_plots)

    if args.save_ids is not None:
        scan_ids = _parse_scan_ids(args.save_ids)
        for scan_id in scan_ids:
            plot_scans(scan_ids=[scan_id], show=False)
            file_name = save_data(
                scan_id=scan_id,
                columns_from_plots=args.columns_from_plots,
                index=args.hide_index_column,
            )
            print('Saved {}'.format(file_name))
