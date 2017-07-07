import re

import matplotlib.pyplot as plt
import numpy as np

from databroker_extractor.common import databroker as dbe
from databroker_extractor.common.plot import clear_plt

d = dbe.activate_beamline_db('smi')

s = dbe.read_single_scan(d, 837)
h = s['scan']
t = h.table()
scan_shape = np.array(h.start.shape)

dets = []
for f in h.fields():
    if re.search('XBPM', f):
        dets.append(f)

for f in dets:
    z = t[f]
    zn = z.reshape(scan_shape)

    plt.imshow(zn, cmap='afmhot')
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    plt.savefig('{}.png'.format(f), dpi=300)
    plt.show()
    clear_plt()
