import numpy as np
from databroker import db, get_fields, get_table
from matplotlib import pyplot as plt

import common.date_time as c_dt
import common.io as c_io
import common.math as c_math
import common.plot as c_plot

X_LABEL = 'bragg'
Y_LABEL = 'VFMcamroi1'


def plot_scans(scan_ids, offset_hours=0, norm=None, x_label=X_LABEL, y_label=Y_LABEL, show=True):
    timestamp = c_dt.current_time(offset_hours=offset_hours, for_file_name=True)
    d = read_scans(scan_ids=scan_ids, x_label=x_label, y_label=y_label)
    y_max = np.array(d['y_list']).max()

    c_plot.clear_plt()

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


def read_scans(scan_ids, x_label=X_LABEL, y_label=Y_LABEL):
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


def read_single_scan(scan_id, x_label=X_LABEL, y_label=Y_LABEL):
    scan = db[scan_id]
    fields = get_fields(scan)
    data = get_table(scan)
    x = np.array(data[x_label])
    y = np.array(data[y_label])
    try:
        fwhm = c_math.calc_fwhm(x, y)
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
        'fwhm': fwhm['fwhm'],
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
    c_io.save_data_pandas(
        file_name=file_name,
        data=d['data'],
        columns=columns,
        index=index,
    )
    return file_name
