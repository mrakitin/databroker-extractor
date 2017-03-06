import datetime
import time

import numpy as np
from databroker import db, get_fields, get_table
from matplotlib import pyplot as plt
from uti_math import fwhm

if __name__ == '__main__':
    timestamp = datetime.datetime.fromtimestamp(time.time() - 5 * 3600).strftime('%Y-%m-%d_%H_%M_%S')

    last_scan = db[-1]
    # last_scan = db[238]
    print(last_scan)

    # Get data:
    data = get_table(last_scan)
    print(data)

    # Get fields:
    fields = list(get_fields(last_scan))
    print(fields)

    # Plot:
    x_label = 'bragg'
    y_label = 'VFMcamroi1'
    x = np.array(data[x_label])
    y = np.array(data[y_label])
    plt.plot(x, y)
    y_norm = (y - np.min(y)) / (np.max(y) - np.min(y)) - 0.5  # roots are at Y=0
    fwhm_value = fwhm(x, y_norm)
    print('FWHM: {}'.format(fwhm_value))

    plt.title(
        'UID:{}\nscan_id: {}  FWHM: {:.5f}'.format(
            last_scan.start.uid,
            last_scan.start.scan_id,
            fwhm_value,
        )
    )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()

    plt.savefig('timestamp_{}_scan_{}.png'.format(timestamp, last_scan.start.scan_id))

    plt.show()
