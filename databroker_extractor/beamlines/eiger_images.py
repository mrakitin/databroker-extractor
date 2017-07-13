# coding: utf-8

import os
import datetime

import h5py
import matplotlib.pyplot as plt
import numpy as np

from metadatastore.mds import MDSRO  # "metadata store read-only"
from filestore.fs import FileStoreRO  # "file store read-only"
from databroker import Broker, get_images, get_events

from chxanalys.chx_packages import get_meta_data, load_data

def save_hdf5(data, filename='data.h5', dataset='dataset'):
    h5f = h5py.File(filename, 'w')
    r = h5f.create_dataset(dataset, data=data)
    status = '{} created: {}'.format(r, os.path.abspath(filename))
    h5f.close()
    return status

def plot_scan(db, uid, mean=True, num=0, log=True, save=True, noplot=True):
    h = db[uid]
    scan_id = h.start.scan_id
    desc = h.start.Measurement
    timestamp = h.start.time
    # print('Timestamp: {}'.format(timestamp))
    time = datetime.datetime.fromtimestamp(timestamp=timestamp).strftime('%Y%m%d%H%M')
    md = get_meta_data(uid)

    imgs = load_data(uid, md['detector'], reverse= True)
    print(uid, scan_id, imgs)
    if save:
        status = save_hdf5(imgs, filename='{}_{}_{}.h5'.format(time, uid, scan_id), dataset='dataset')
        print(status)

    if noplot:
        return
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if log:
        ax.imshow(np.log10(imgs[num]) if not mean else np.log10(np.mean(imgs, axis=0)))
    else:
        ax.imshow(imgs[num] if not mean else np.mean(imgs, axis=0))
    ax.set_title('UID: {}, scan_id: {}\n{}'.format(uid, scan_id, desc))
    plt.show()

def clear_plt():
    """Clear the plots (useful when plotting in a loop).

    :return: None
    """
    plt.cla()
    plt.clf()
    plt.close()


if __name__ == '__main__':
    # This an example. You'll need to know your local configuration.
    mds = MDSRO({'host': 'localhost',
                 'port': 27017,
                 'database': 'datastore',
                 'timezone': 'US/Eastern'})

    # This an example. You'll need to know your local configuration.
    fs = FileStoreRO({'host': 'localhost',
                      'port': 27017,
                      'database': 'filestore'})

    db = Broker(mds, fs)

    scans = [
        # 6/27/ 12:04 -12:10 am: three datasets using the mono beam slits in the FOE (S2 in the virtual beamline) as a pinhole with nominal size 7x7um, 10x10um and 13x13um, scattering collected with the Eiger4M detector (this is our detector used in experiments) at 16m (exact distance is in the datafile). Every count in these files is a real photon (photon counting, noise-free detector).        
        'fb8686', '778504', 'd6705c',
        # 6/26 11:02 - 11:40pm measurement of lithographic sample 'random posts II' under various coherence conditions (using S2 = mbs to select parts of the wavefront, the same way we do in 'real' experiments). Beam is focused in the same way as we do for experiments (standard setup for virtual beamline, focal sizes were measured in April with fluorescent knife edge). I have each measurement with and without flatfield correction on the detector, but that's more for data processing on our side.
        '889602', 'd30077', '9e70ac', 'd18bff', 
        # 'b02a6d',
        'b0f7ce', 'dc3eb8', '169428',
        # 6/26 9:57 - 10:28 X-ray energy: 9.65 keV measurement of lithographic sample 'random posts I', same conditions as described above.
        '19efca', '3dbf3e', '452b7d', '101631', 'd77696', '69c533', '1a9415', '541142',
    ]
    
    for s in scans:
        print('Scan: {}'.format(s))
        plot_scan(db, s)
    
