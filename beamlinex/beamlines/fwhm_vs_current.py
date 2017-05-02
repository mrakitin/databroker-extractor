import numpy as np
from matplotlib import pyplot as plt

from beamlinex.common.databroker import read_single_scan
from beamlinex.common.io import save_data_numpy
from beamlinex.common.plot import clear_plt


def fwhm_vs_current(scans, reverse=False, current='mean', show=True, convert_to_energy=False, material=None,
                    x_label='dcm_bragg', y_label='VFMcamroi1', beamline='SMI', ring_currents=None, harmonic=None):
    allowed_current_values = ('mean', 'peak', 'first', 'last')
    if current not in allowed_current_values:
        raise ValueError('{}: not allowed. Allowed values: {}'.format(current, allowed_current_values))

    print('Scans list:\n{}'.format(scans))

    fwhm_vs_current = np.zeros((len(scans), 2))
    fname = '{}_fwhm_vs_current_{}_to_{}'.format(beamline.lower(), scans[0], scans[-1])
    for i, s in enumerate(scans):
        print('s={}'.format(s))
        d = read_single_scan(
            s,
            x_label=x_label,
            y_label=y_label,
            convert_to_energy=convert_to_energy,
            material=material
        )
        fwhm = d['fwhm']

        if not ring_currents:
            if current == 'mean':
                ring_current = np.mean(d['data']['ring_current'])
            else:
                if current == 'peak':
                    idx = d['data'][y_label].argmax()
                elif current == 'first':
                    idx = 0
                elif current == 'last':
                    idx = -1
                ring_current = list(d['data']['ring_current'])[idx]
        else:
            current = 'manual'
            ring_current = ring_currents[i]

        fwhm_vs_current[i, 0] = ring_current
        fwhm_vs_current[i, 1] = fwhm

    # Save data:
    save_data_numpy(
        data=fwhm_vs_current,
        name='{}.dat'.format(fname),
        header='ring_current    fwhm'
    )

    units = 'eV' if convert_to_energy else 'deg'

    # Plotting:
    plt.figure(figsize=(16, 10))
    plt.grid()
    title = beamline
    if harmonic:
        title = '{}: {}'.format(beamline, harmonic)
    plt.title(title)
    plt.xlabel('Ring current [mA] (current={})'.format(current))
    plt.ylabel('FWHM [{}]'.format(units))
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
    beamline = 'SMI'
    # beamline = 'CHX'

    allowed_beamlines = ('SMI', 'CHX')
    if beamline not in allowed_beamlines:
        raise ValueError('Beamline "{}" is not allowed. Allowed beamlines: {}'.format(beamline, allowed_beamlines))

    first = None
    last = None
    exclude = None

    if beamline == 'SMI':
        # x_label = 'dcm_bragg'
        x_label = 'bragg'
        y_label = 'VFMcamroi1'

        # SMI measurements on 03/18/2017:
        # harmonic = '7th harmonic'
        # scans_list = [338, 343, 344, 345, 353, 354, 355, 361, 362, 364, 367, 368, 369, 375, 376, 377, 378, 379, 380,
        #               381]
        # ring_currents = [4.8, 9, 8.766, 17.28, 19.963, 18.64, 26.281, 29.215, 28.442, 36.439, 40.425, 39.378, 38.367,
        #                  48.681, 47.281, 46.019, 44.719, 43.538, 42.417, 41.303]

        # harmonic = '17th harmonic'
        # scans_list = [339, 342, 346, 349, 350, 352, 356, 360, 366, 370, 372, 373]
        # ring_currents = [4.5, 9.3, 16.504, 15.229, 14.974, 20.976, 24.866, 30.532, 34.113, 37.123, 35.491, 53.225]

        harmonic = '18th harmonic'
        scans_list = [340, 341, 347, 348, 351, 357, 358, 359, 363, 365, 371, 374]
        ring_currents = [4.4, 9.4, 16.182, 15.732, 21.324, 24.279, 23.767, 31.044, 27.468, 34.721, 36.153, 50.816]


        # # SMI measurements on 04/04/2017:
        # first = 418
        # last = 657
        # exclude = [529] + list(range(565, 584))
        # scans_list = None
        # ring_currents = None
        # harmonic = None

    else:  # beamline == 'CHX':
        x_label = 'dcm_b'
        y_label = 'xray_eye1_stats1_total'

        # CHX measurements on 03/18/2017:
        harmonic = '7th harmonic'
        scans_list = [19041, 19042, 19045, 19046, 19049, 19050, 19053, 19054, 19057]
        ring_currents = [4.84167, 9.44619, 15.18044, 20.93994, 23.91838, 30.37130, 32.92343, 39.49573, 48.11848]

        # harmonic = '11th harmonic'
        # scans_list = [19040, 19043, 19044, 19047, 19048, 19051, 19052, 19055, 19056]
        # ring_currents = [5.04095, 8.93891, 17.08810, 19.20807, 25.97480, 26.80035, 36.00833, 35.39244, 52.94804]

    if not scans_list:
        scans = []
        for i in range(first, last + 1):
            if not i in exclude:
                scans.append(i)
    else:
        scans = scans_list

    reverse = False

    # current = 'mean'
    current = 'peak'
    # current = 'first'
    # current = 'last'

    show = True
    # convert_to_energy = False
    convert_to_energy = True
    material = 'Si111cryo'

    # for current in ('mean', 'peak', 'first', 'last'):
    #     smi_fwhm_vs_current(reverse=reverse, current=current, show=show)

    fwhm_vs_current(
        scans,
        reverse=reverse,
        current=current,
        show=show,
        convert_to_energy=convert_to_energy,
        material=material,
        beamline=beamline,
        x_label=x_label,
        y_label=y_label,
        ring_currents=ring_currents,
        harmonic=harmonic
    )
