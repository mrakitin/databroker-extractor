import matplotlib.pyplot as plt
import numpy as np

from databroker_extractor.common import databroker as dbe


def normalize(y, shift=0.0):
    return (y - np.min(y)) / (np.max(y) - np.min(y)) - shift


if __name__ == '__main__':
    d = dbe.activate_beamline_db('smi')

    a = dbe.read_single_scan(d, 310)
    b = dbe.read_single_scan(d, 929)

    x_a = a['data']['bragg']
    y_a = a['data']['VFMcamroi1']

    y_b = b['data']['FScamroi4']
    x_b = b['data']['energy_bragg']

    diff = (float(x_a[np.where(y_a == y_a.max())[0]]) - float(x_b[np.where(y_b == y_b.max())[0]])) * 1.2

    plt.plot(x_b, normalize(y_b), label='scan {}'.format(b['scan']['start']['scan_id']))
    plt.plot(x_a - diff, normalize(y_a), label='scan {}'.format(a['scan']['start']['scan_id']))

    plt.legend()
    plt.grid()
    plt.show()
