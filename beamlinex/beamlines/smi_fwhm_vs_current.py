import numpy as np
from matplotlib import pyplot as plt

from beamlinex.common.databroker import read_single_scan
from beamlinex.common.io import save_data_numpy
from beamlinex.common.plot import clear_plt


def smi_fwhm_vs_current(reverse=False, current='mean', show=True):
    allowed_current_values = ('mean', 'peak', 'first', 'last')
    if current not in allowed_current_values:
        raise ValueError('{}: not allowed. Allowed values: {}'.format(current, allowed_current_values))

    exclude = [529] + list(range(565, 584))

    first = 418
    last = 657

    scans = []
    for i in range(first, last + 1):
        if not i in exclude:
            scans.append(i)

    print('Scans list:\n{}'.format(scans))

    fwhm_vs_current = np.zeros((len(scans), 2))
    fname = 'smi_fwhm_vs_current_{}_to_{}'.format(scans[0], scans[-1])
    for i, s in enumerate(scans):
        print('s={}'.format(s))
        d = read_single_scan(s, x_label='dcm_bragg', y_label='VFMcamroi1')
        fwhm = d['fwhm']
        if current == 'mean':
            ring_current = np.mean(d['data']['ring_current'])
        else:
            if current == 'peak':
                idx = d['data']['VFMcamroi1'].argmax()
            elif current == 'first':
                idx = 0
            elif current == 'last':
                idx = -1
            ring_current = list(d['data']['ring_current'])[idx]
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
    plt.xlabel('Ring current [mA] (current={})'.format(current))
    plt.ylabel('FWHM [deg]')
    if reverse:
        plt.xlim(fwhm_vs_current[0, 0], fwhm_vs_current[-1, 0])
    plt.scatter(fwhm_vs_current[:, 0], fwhm_vs_current[:, 1], s=200)
    plt.tight_layout()
    plt.savefig('{}_current={}.png'.format(fname, current))
    if show:
        plt.show()
    clear_plt()
    print('')


if __name__ == '__main__':
    reverse = False

    # current = 'mean'
    current = 'peak'
    # current = 'first'
    # current = 'last'

    show = True

    # for current in ('mean', 'peak', 'first', 'last'):
    #     smi_fwhm_vs_current(reverse=reverse, current=current, show=show)

    smi_fwhm_vs_current(reverse=reverse, current=current, show=show)
