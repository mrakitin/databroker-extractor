def parse_scan_ids(scans_list):
    try:
        scan_ids = [int(x) for x in scans_list]
    except:
        raise ValueError('Incorrect scan ids provided: {}'.format(scans_list))
    if not scan_ids:
        scan_ids = [-1]
    return scan_ids
