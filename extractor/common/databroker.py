#!/usr/bin/python
# -*- coding: utf-8 -*-

import databroker as db
import numpy as np

import extractor.common.math as c_math
import chxtools.xfuncs as xf  # from https://github.com/NSLS-II-CHX/chxtools/blob/master/chxtools/xfuncs.py


def check_columns(data, columns):
    if columns is None:
        return True
    available_columns = list(data.columns)
    for c in columns:
        if c not in available_columns:
            raise ValueError('{}: invalid column(s). Available columns: {}'.format(c, available_columns))
    return True


def get_scans_list(keyword):
    """Get a list of scan filtered by the provided keyword.

    :param keyword: a keyword to search scans.
    :return: a list of found scans.
    """
    return db.db(keyword)


def read_scans(scan_ids, x_label, y_label, **kwargs):
    real_scan_ids = []
    uids = []
    x_list = []
    y_list = []
    fwhm_values = []
    beamline_id = None
    for scan_id in scan_ids:
        d = read_single_scan(scan_id=scan_id, x_label=x_label, y_label=y_label, **kwargs)
        if not beamline_id:
            beamline_id = d['beamline_id']
        real_scan_ids.append(d['scan_id'])
        uids.append(d['uid'])
        x_list.append(d['x'])
        y_list.append(d['y'])
        fwhm_values.append(d['fwhm'])

    return {
        'beamline_id': beamline_id,
        'real_scan_ids': real_scan_ids,
        'uids': uids,
        'x_list': x_list,
        'y_list': y_list,
        'fwhm_values': fwhm_values,
    }


def read_single_scan(scan_id, x_label=None, y_label=None, convert_to_energy=False, material=None, delta_bragg=None,
                     d_spacing=None):
    s = scan_info(scan_id=scan_id)

    scan = db.db[scan_id]
    fields = db.get_fields(scan)
    data = scan_data(scan_id)
    if x_label is not None:
        if check_columns(data=data, columns=[x_label]):
            delta_bragg = 0.0 if not delta_bragg else float(delta_bragg)
            if d_spacing:
                d_spacing = float(d_spacing)
            x = np.array(data[x_label]) + delta_bragg
    else:
        x = None
    if convert_to_energy:
        x = xf.get_EBragg(material, theta_Bragg=np.abs(x), d_spacing=d_spacing) * 1e3  # keV -> eV
    if y_label is not None:
        if check_columns(data=data, columns=[y_label]):
            y = np.array(data[y_label])
        else:
            y = None
    try:
        fwhm = c_math.calc_fwhm(x, y)['fwhm']
    except:
        fwhm = -1

    return {
        'scan': scan,
        'beamline_id': s.beamline_id,
        'scan_id': s.scan_id,
        'uid': s.uid,
        'fields': fields,
        'data': data,
        'x': x,
        'y': y,
        'x_label': x_label,
        'y_label': y_label,
        'fwhm': fwhm,
    }


def scan_data(scan_id):
    scan = db.db[scan_id]
    return db.get_table(scan)


def scan_info(scan_id):
    scan = db.db[scan_id]
    return scan.start
