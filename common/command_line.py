#!/usr/bin/python
# -*- coding: utf-8 -*-

def parse_range_ids(range_str):
    range_list = range_str.split(':')
    assert len(range_list) == 2, \
        '{}: provided value is incorrect. The value must consist of two integers separated by colon.'.format(range_str)
    first_id = int(range_list[0])
    last_id = int(range_list[1])
    assert last_id >= first_id, 'Got first id ({}) > last id ({})'.format(first_id, last_id)
    return list(range(first_id, last_id + 1))


def parse_scan_ids(scans_list):
    try:
        scan_ids = [int(x) for x in scans_list]
    except:
        raise ValueError('Incorrect scan ids provided: {}'.format(scans_list))
    if not scan_ids:
        scan_ids = [-1]
    return scan_ids
