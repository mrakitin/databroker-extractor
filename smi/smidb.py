import datetime
import time

import numpy as np
from databroker import db, get_fields, get_table
from matplotlib import pyplot as plt
from uti_math import fwhm as calc_fwhm


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


def save_data(scan_id):
    d = read_single_scan(scan_id)
    file_name = 'scan_{}.dat'.format(scan_id)
    data = np.zeros((len(d['x']), 2))
    data[:, 0] = d['x']
    data[:, 1] = d['y']
    np.savetxt(file_name, data, fmt='%10.6f %8d', header='{:12s} {:8s}'.format(d['x_label'], d['y_label']))
    return file_name


def _clear_plt():
    """Clear the plots (useful when plotting in a loop).

    :return: None
    """
    plt.cla()
    plt.clf()
    plt.close()


if __name__ == '__main__':
    plot_graphs = True
    save_data_files = False

    if plot_graphs:
        scan_ids = range(243, 255)
        # scan_ids = [-3, -2]
        norm = None
        # norm = 'total'
        # norm = 'individual'
        plot_scans(scan_ids=scan_ids, norm=norm)

    if save_data_files:
        scan_ids = range(243, 259 + 1)
        for scan_id in scan_ids:
            plot_scans(scan_ids=[scan_id], show=False)
            file_name = save_data(scan_id)
            print('Saved {}'.format(file_name))
