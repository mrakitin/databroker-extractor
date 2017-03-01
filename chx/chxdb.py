"""
This is a library for experimental data processing from the CHX beamline of NSLS-II. It requires the SRW utils library,
please download https://github.com/ochubar/SRW/blob/master/env/work/srw_python/uti_math.py#L615 and add it to your
PYTHONPATH environment variable.
"""

import datetime

import numpy as np
from databroker import db, get_fields, get_images, get_table
from matplotlib import pyplot as plt
from uti_math import fwhm


def get_and_plot(scan_id, save=False, gap_field='', idx=None):
    g, e, t = get_data(scan_id, gap_field=gap_field)
    plot_scan(g, e, scan_id=scan_id, timestamp=t, save=save, gap_field=gap_field, idx=idx)


def get_data(scan_id, gap_field='ivu_gap', energy_field='elm_sum_all', det=None, debug=False):
    scan, t = get_scan(scan_id)
    if det:
        imgs = get_images(scan, det)
        im = imgs[-1]
        if debug:
            print(im)

    table = get_table(scan)
    fields = get_fields(scan)

    if debug:
        print(table)
        print(fields)
    gaps = table[gap_field]
    energies = table[energy_field]

    return gaps, energies, t


def get_scan(scan_id, debug=False):
    scan = db[scan_id]
    t = datetime.datetime.fromtimestamp(scan['start']['time']).strftime('%Y-%m-%d %H:%M:%S')
    if debug:
        print(scan)
    print('Scan ID: {}  Timestamp: {}'.format(scan_id, t))
    return scan, t


def plot_scan(x, y, scan_id, timestamp, save, gap_field, idx):
    x = np.array(x)
    y = np.array(y)
    if gap_field == 'ivu_gap':
        units = 'mm'
    elif gap_field == 'dcm_b':
        units = 'deg'
    else:
        raise ValueError('Unknown field: {}'.format(gap_field))
    try:
        y_norm = (y - np.min(y)) / (np.max(y) - np.min(y)) - 0.5  # roots are at Y=0
        fwhm_value = fwhm(x, y_norm)
    except Exception:
        fwhm_value = -1

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111)
    ax.scatter(x, y)
    ax.grid()
    ax.set_title('Scan ID: {}    Timestamp: {}\nFWHM: {:.5f} {}'.format(scan_id, timestamp, fwhm_value, units))
    xlabel = gap_field.replace('_', ' ')

    ax.set_xlabel('{} [{}]'.format(xlabel, units))
    ax.set_ylabel('Intensity [arb. units]')
    if not save:
        plt.show()
    else:
        if idx is not None:
            plt.savefig('scan_{:02d}_{}.png'.format(idx, scan_id))
        else:
            plt.savefig('scan_{}.png'.format(scan_id))


if __name__ == '__main__':
    # This may be used if the configuration is not set via ~/.config. See the following documentation for more details:
    # http://nsls-ii.github.io/databroker/configuration.html
    '''
    from metadatastore.mds import MDSRO  # metadata store read-only
    from filestore.fs import FileStoreRO  # file store read-only
    from databroker import Broker, DataBroker as db, get_images, get_table, get_events, get_fields

    # This an example. You'll need to know your local configuration.
    mds = MDSRO({'host': 'localhost',
                 'port': 27018,
                 'database': 'datastore',
                 'timezone': 'US/Eastern'})

    # This an example. You'll need to know your local configuration.
    fs = FileStoreRO({'host': 'localhost',
                      'port': 27018,
                      'database': 'filestore'})

    db1 = Broker(mds, fs)
    '''

    # scan_id = -1
    # scan_id = '31a8fc'
    # detector = 'xray_eye3_image'

    harmonics_scan = False
    intensity_scan = True

    if harmonics_scan:
        # Harmonics scan:
        scan_ids = [
            # center vertical mbs on ID cone:	0.6x1.2 (pbs)		17585 (scan#)		date: 02/28/2017
            # ID harmonic: 5th	energy: 9.65keV		gap: 6.640
            # Ti foil, elm: 	50pC, .1s	.05x.05,.1x.4
            #     100pC, .1s	.2x.4
            ('1eff511d', 'ivu_gap'),
            ('8f6a6004', 'ivu_gap'),
            ('1f1422b4', 'ivu_gap'),
            ('7949f1b0', 'dcm_b'),
            ('daeb15e3', 'dcm_b'),
            ('6edfa33a', 'dcm_b'),
            # center vertical mbs on ID cone:	0.6x1.2 (pbs)	.4x.1 (mbs)	 17599 (scan#)
            # ID harmonic: 7th	energy: 9.75keV		gap: 5.240	can't scan gap at 9.65keV…
            # Ti foil, elm: 	50pC, .1s	.05x.05,.1x.4
            #     100pC, .1s	.2x.4
            ('74798cb6', 'ivu_gap'),
            ('dc2b5045', 'ivu_gap'),
            ('c4f95268', 'ivu_gap'),
            ('b2365717', 'dcm_b'),
            ('ac99ddd0', 'dcm_b'),
            ('b808a890', 'dcm_b'),
            # center vertical mbs on ID cone:	0.6x1.2 (pbs)	.4x.1 (mbs)	 17610 (scan#)
            # gap scan: #17613
            # ID harmonic: 7th	energy: 9.65keV		gap: 5.2017
            # Ti foil, elm: 	50pC, .1s	.05x.05,.1x.4
            #     100pC, .1s	.2x.4
            ('e23fb7a1', 'dcm_b'),
            ('afc6da9e', 'dcm_b'),
            ('e71b8b5f', 'dcm_b'),
        ]

        save = True
        # save = False

        for i, scan_id in enumerate(scan_ids):
            get_and_plot(scan_id[0], save=save, gap_field=scan_id[1], idx=i)

    if intensity_scan:
        scan_id = '58732824'
        scan, t = get_scan(scan_id)
        images = get_images(scan, 'xray_eye3_image')
        print(images)
