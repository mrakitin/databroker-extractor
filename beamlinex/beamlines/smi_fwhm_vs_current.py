import numpy as np
from matplotlib import pyplot as plt

from beamlinex.common.databroker import read_single_scan
from beamlinex.common.io import save_data_numpy


def smi_fwhm_vs_current(reverse=False):
    remove = 529
    first = 530  # 418
    last = 560
    scans = list(range(first, remove)) + list(range(remove + 1, last + 1))
    fwhm_vs_current = np.zeros((len(scans), 2))
    fname = 'smi_fwhm_vs_current_{}_to_{}'.format(scans[0], scans[-1])
    for i, s in enumerate(scans):
        print('s={}'.format(s))
        d = read_single_scan(s, x_label='dcm_bragg', y_label='VFMcamroi1')
        fwhm = d['fwhm']
        ring_current = list(d['data']['ring_current'])[-1]
        fwhm_vs_current[i, 0] = ring_current
        fwhm_vs_current[i, 1] = fwhm

    # Save data:
    save_data_numpy(
        data=fwhm_vs_current,
        name='{}.dat'.format(fname),
        header='ring_current    fwhm'
    )

    # Plotting:
    plt.figure(figsize=(16, 10))
    plt.grid()
    plt.xlabel('Ring current [mA]')
    plt.ylabel('FWHM [deg]')
    if reverse:
        plt.xlim(fwhm_vs_current[0, 0], fwhm_vs_current[-1, 0])
    plt.plot(fwhm_vs_current[:, 0], fwhm_vs_current[:, 1])
    plt.tight_layout()
    plt.savefig('{}.png'.format(fname))
    plt.show()

    print('')


if __name__ == '__main__':
    reverse = False
    smi_fwhm_vs_current(reverse)
