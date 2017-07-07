import re

import matplotlib.pyplot as plt
import numpy as np

from databroker_extractor.common import databroker as dbe
from databroker_extractor.common.plot import clear_plt


def plot_2d_scans(beamline='smi', scan_id=None, dets_pattern='XBPM', imsave=False, cmap='afmhot', dpi=300, show=False,
                  image_format='png'):
    """Plot 2d scan images.

    :param beamline: beamline of interest.
    :param scan_id: particular scan_id.
    :param dets_pattern: pattern of the detectors names in the fields of the databroker header.
    :param imsave: flag to save the image by means of imsave function.
    :param cmap: color map to use.
    :param dpi: resolution.
    :param show: flag to show the resulted image.
    :return: None.
    """

    # Activade databroker for the specified beamline:
    d = dbe.activate_beamline_db(beamline=beamline)

    # Read the scan:
    s = dbe.read_single_scan(d, scan_id=scan_id)
    h = s['scan']
    t = h.table()
    scan_shape = np.array(h.start.shape)

    # Get the list of detectors of interest:
    dets = []
    for f in h.fields():
        if re.search(dets_pattern, f):
            dets.append(f)

    for f in dets:
        z = t[f]
        zn = z.values.reshape(scan_shape)

        fname = '{}.{}'.format(f, image_format)

        plt.imshow(zn, cmap=cmap)
        plt.xticks([])
        plt.yticks([])
        plt.tight_layout()
        if imsave:
            plt.imsave(fname, zn, cmap=cmap, dpi=dpi)
        else:
            plt.savefig(fname, dpi=dpi)

        if show:
            plt.show()
        clear_plt()


if __name__ == '__main__':
    plot_2d_scans(beamline='smi', scan_id=837, imsave=False)
