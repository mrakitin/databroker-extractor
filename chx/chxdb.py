import datetime
from metadatastore.mds import MDSRO  # metadata store read-only
from filestore.fs import FileStoreRO  # file store read-only
from databroker import db, get_images, get_table, get_events, get_fields

'''
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

def get_scan(scan_id, gap_field='ivu_gap', energy_field='elm_sum_all', det=None, debug=False):
    scan = db[scan_id]
    t = datetime.datetime.fromtimestamp(scan['start']['time']).strftime('%Y-%m-%d %H:%M:%S')

    if debug:    
        print(scan)
    print('\nTimestamp: {}'.format(t))

    if det:
        imgs = get_images(scan, detector)
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

    return gaps, energies


def plot_scan(x, y):
    plt.scatter(x, y)
    plt.show()


def get_and_plot(scan_id):
    g, e = get_scan(scan_id)
    plot_scan(g, e)


if __name__ == '__main__':
    # scan_id = -1
    # scan_id = '31a8fc'
    scan_id = '1eff511d'
    # detector = 'xray_eye3_image'

    g, e = get_scan(scan_id)
    plot_scan(g, e)
