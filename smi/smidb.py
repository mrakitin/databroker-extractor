import datetime
import time

import numpy as np
from databroker import db, get_fields, get_table
from matplotlib import pyplot as plt
from uti_math import fwhm

if __name__ == '__main__':
    timestamp = datetime.datetime.fromtimestamp(time.time() - 5 * 3600).strftime('%Y-%m-%d_%H_%M_%S')

    # scan_ids = [243, 255]
    scan_ids = [255, 243]
    scans = []
    data_list = []
    fwhm_values = []
    x_label = 'bragg'
    y_label = 'VFMcamroi1'
    for scan_id in scan_ids:
        scan = db[scan_id]
        data = get_table(scan)

        scans.append(scan)
        data_list.append(data)

        # Get fields:
        fields = list(get_fields(scan))
        print('scan_id: {}'.format(scan.start.scan_id))

    # y_max = np.array([x[y_label] for x in data_list]).max()
    y_max = 1
    for i, scan_id in enumerate(scan_ids):
        x = np.array(data_list[i][x_label])
        y = np.array(data_list[i][y_label])

        y_norm = (y - np.min(y)) / (np.max(y) - np.min(y)) - 0.5  # roots are at Y=0
        try:
            fwhm_value = fwhm(x, y_norm)
        except:
            fwhm_value = -1
        fwhm_values.append(fwhm_value)

        # Plot:
        plt.plot(x, y / y_max, label='scan_id={},\nFWHM={:.5f}'.format(scans[i].start.scan_id, fwhm_value))

    plt.legend()

    plt.title(
        'UID:{}\nscan_id: {}'.format(
            scans[-1].start.uid,
            ', '.join([str(x.start.scan_id) for x in scans]),
        )
    )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()

    plt.savefig('timestamp_{}_scan_{}.png'.format(timestamp, scans[-1].start.scan_id))

    plt.show()
