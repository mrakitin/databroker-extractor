from databroker import db

import common.date_time as c_dt


def get_scan(scan_id, debug=False):
    """Get scan from databroker using provided scan id.

    :param scan_id: scan id from bluesky.
    :param debug: a debug flag.
    :return: a tuple of scan and timestamp values.
    """
    scan = db[scan_id]
    t = c_dt.humanize_time(timestamp=scan['start']['time'])
    if debug:
        print(scan)
    print('Scan ID: {}  Timestamp: {}'.format(scan_id, t))
    return scan, t


def get_scans_list(keyword):
    """Get a list of scan filtered by the provided keyword.

    :param keyword: a keyword to search scans.
    :return: a list of found scans.
    """
    return db(keyword)
