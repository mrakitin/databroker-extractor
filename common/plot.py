#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

import common.databroker as c_db
import common.date_time as c_dt
import common.io as c_io


def plot_scans(scan_ids, x_label, y_label, x_units=None, y_units=None, norm=None, save=True, show=True, scatter_size=10,
               figsize=(10, 7.5), extension='png', convert_to_energy=False, material='Si111cryo', **kwargs):
    assert len(scan_ids) >= 1, 'The number of scan ids is empty'
    d = c_db.read_scans(scan_ids=scan_ids, x_label=x_label, y_label=y_label,
                        convert_to_energy=convert_to_energy, material=material)

    s_first = c_db.scan_info(scan_id=scan_ids[0])
    if len(scan_ids) == 1:
        str_scan_id = s_first.scan_id
    else:
        s_last = c_db.scan_info(scan_id=scan_ids[-1])
        str_scan_id = '{}-{}'.format(s_first.scan_id, s_last.scan_id)

    file_name = c_io.format_filename(
        beamline_id=s_first.beamline_id,
        scan_id=str_scan_id,
        extension=extension,
        timestamp=c_dt.scan_timestamp(scan_id=s_first.scan_id, **kwargs),
    )

    y_max = np.hstack(d['y_list']).max()

    clear_plt()

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)

    orig_x_label = x_label
    orig_x_units = x_units
    if convert_to_energy:
        x_label = 'Photon energy'
        x_units = 'eV'

    for i in range(len(scan_ids)):
        x = d['x_list'][i]
        y = d['y_list'][i]
        if norm == 'total':
            y = y / y_max
        elif norm == 'individual':
            y = y / np.array(d['y_list'][i]).max()
        elif norm is None:
            pass
        else:
            raise ValueError('{}: the provided normalization method is not implemented.'.format(norm))
        ax.scatter(x, y, s=scatter_size, label='scan_id={},\nFWHM={:.5f} {}'.format(
            d['real_scan_ids'][i],
            d['fwhm_values'][i],
            x_units,
        ))
        ax.plot(x, y, '--')

    ax.legend()

    ax.set_title(
        'UID:{}\nscan_id: {}'.format(
            d['uids'][-1],
            ', '.join([str(x) for x in d['real_scan_ids']]),
        )
    )

    ax.set_xlabel(_format_label(x_label, x_units, orig_label=orig_x_label, orig_units=orig_x_units))
    ax.set_ylabel(_format_label(y_label, y_units))
    ax.grid()

    plt.tight_layout()
    if save:
        plt.savefig(file_name)

    if show:
        plt.show()


def save_raw_image(data, name):
    im = Image.fromarray(data).convert('L')
    im.save(name)


def clear_plt():
    """Clear the plots (useful when plotting in a loop).

    :return: None
    """
    plt.cla()
    plt.clf()
    plt.close()


def _format_label(label, units, orig_label=None, orig_units=None):
    if label == orig_label:
        orig_label = None
    label = '{} [{}]'.format(label, units) if units else label
    if orig_label and orig_units:
        label = '{} (orig. label: {} [{}])'.format(label, orig_label, orig_units)
    return label
