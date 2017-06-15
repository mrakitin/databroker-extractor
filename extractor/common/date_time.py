#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time

import extractor.common.databroker as c_db


def current_timestamp():
    return time.time()


def current_time(offset_hours=0, **kwargs):
    return humanize_time(current_timestamp() + offset_hours * 3600, **kwargs)


def humanize_time(timestamp, time_format='%Y-%m-%d %H:%M:%S', for_file_name=False):
    if for_file_name:
        time_format = '%Y-%m-%d_%H-%M-%S'
    return datetime.datetime.fromtimestamp(timestamp=timestamp).strftime(time_format)


def scan_timestamp(scan_id, timestamp):
    allowed_values = (None, 'scan', 'current')
    if timestamp is None:
        t = ''
    elif timestamp == 'scan':
        s = c_db.scan_info(scan_id=scan_id)
        t = s.time
    elif timestamp == 'current':
        t = current_timestamp()
    else:
        raise ValueError('{}: incorrect value. Allowed values: {}'.format(timestamp, allowed_values))
    return t
