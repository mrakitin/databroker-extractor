#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

import common.databroker as c_db
import common.date_time as c_dt


def format_filename(beamline_id, scan_id, extension='', timestamp=None):
    args = [beamline_id.lower()]
    format_name = '{}'
    if timestamp:
        timestamp = c_dt.humanize_time(timestamp=timestamp, for_file_name=True)
        args.append(timestamp)
        format_name += '_{}'
    format_name += '_scan_{}.{}'
    args.append(scan_id)
    return format_name.format(*args, extension)


def save_data(scan_id, columns=None, index=False, extension='dat', **kwargs):
    """Save data to a file.

    :param scan_id: scan id to save data for.
    :param columns: columns to print (set to 'None' to output all columns).
    :param index: if to print the index column.
    :param extension: extension of the file.
    :return file_name: name of the saved file.
    """
    s = c_db.scan_info(scan_id=scan_id)
    file_name = format_filename(
        beamline_id=s.beamline_id,
        scan_id=s.scan_id,
        extension=extension,
        timestamp=c_dt.scan_timestamp(scan_id=scan_id, **kwargs),
    )

    save_data_pandas(
        file_name=file_name,
        data=c_db.scan_data(scan_id=scan_id),
        columns=columns,
        index=index,
    )
    return file_name


def save_data_pandas(file_name, data, columns, index, justify='left'):
    if c_db.check_columns(data=data, columns=columns):
        with open(file_name, 'w') as f:
            f.write(data.to_string(columns=columns, index=index, justify=justify))


def save_data_numpy(data, name, header=None):
    kwargs = {}
    if header:
        kwargs['header'] = header
    np.savetxt(
        name,
        data,
        **kwargs
    )
