import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from beamlinex.common.command_line import read_config
from beamlinex.common.databroker import read_single_scan
from beamlinex.common.fit_data import fit_data, plot_data
from beamlinex.common.io import save_data_pandas
from beamlinex.common.plot import clear_plt


def fwhm_vs_current(scans, reverse=False, current='mean', show=True, convert_to_energy=False, material=None,
                    x_label='dcm_bragg', y_label='VFMcamroi1', beamline='SMI', ring_currents=None, harmonic=None,
                    mode=None, num_bunches=None, delta_bragg=None, d_spacing=None, **kwargs):
    allowed_current_values = ('mean', 'peak', 'first', 'last')
    if current not in allowed_current_values:
        raise ValueError('{}: not allowed. Allowed values: {}'.format(current, allowed_current_values))

    print('Scans list:\n{}'.format(scans))

    data = []
    columns = ['timestamp', 'current_per_bunch', 'fwhm']
    if mode:
        columns.append('espread')
    fname = '{}_fwhm_vs_current_{}_to_{}'.format(beamline.lower(), scans[0], scans[-1])
    for i, s in enumerate(scans):
        print('s={}'.format(s))
        d = read_single_scan(
            s,
            x_label=x_label,
            y_label=y_label,
            convert_to_energy=convert_to_energy,
            material=material,
            delta_bragg=delta_bragg,
            d_spacing=d_spacing
        )
        fwhm = d['fwhm']
        espread = fwhm2espread(fwhm, mode=mode, **kwargs) if mode else None

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

        data.append([np.array(d['data']['time'])[i], ring_current / float(num_bunches), fwhm])
        if espread:
            data[-1].append(espread)

    # Convert data to pandas dataframe:
    data = pd.DataFrame(data, columns=columns)

    # Save data:
    file_name = '{}.dat'.format(fname)
    save_data_pandas(file_name, data, columns, index=True, justify='right')

    if convert_to_energy:
        units = 'eV' if not mode else ''
    else:
        units = 'deg'

    # Plotting:
    plt.figure(figsize=(16, 10))
    plt.grid()
    title = beamline
    if harmonic:
        title = '{}: {}'.format(beamline, harmonic)
    plt.title(title)
    if not mode:
        plt.xlabel('Ring current [mA] (current={})'.format(current))
        plt.ylabel('FWHM [{}]'.format(units))
        if reverse:
            plt.xlim(data['current_per_bunch'][0], data['current_per_bunch'][-1])
        plt.scatter(data['current_per_bunch'], data['fwhm'], s=200)
    else:
        plt.xlabel('Ring current per bunch [mA]')
        plt.ylabel(r'Energy spread, $10^{-3}$')
        plt.scatter(data['current_per_bunch'], data['espread'], s=100)
        plt.ylim(
            (data['espread'].min() - np.abs(data['espread'].min()) * 0.01),
            (data['espread'].max() + np.abs(data['espread'].max()) * 0.01)
        )
    plt.tight_layout()
    plt.savefig('{}.png'.format(fname))
    if show:
        plt.show()
    clear_plt()
    print('')


def main(beamline, **kwargs):
    allowed_beamlines = read_config()
    if beamline not in allowed_beamlines:
        raise ValueError('Beamline "{}" is not allowed. Allowed beamlines: {}'.format(beamline, allowed_beamlines))

    first = None
    last = None
    exclude = None

    mode = None

    show = True
    # convert_to_energy = False
    convert_to_energy = True
    material = 'Si111cryo'
    delta_bragg = None
    d_spacing = None

    if beamline.upper() == 'SMI':
        # x_label = 'dcm_bragg'
        x_label = 'bragg'
        y_label = 'VFMcamroi1'

        # SMI measurements on 03/18/2017:
        harmonic = '7th harmonic'
        # mode = 'reg'
        # scans_list = [338, 343, 344, 345, 353, 354, 355, 361, 362, 364, 367, 368, 369, 375, 376, 377, 378, 379, 380,
        #               381]
        # ring_currents = [4.8, 9, 8.766, 17.28, 19.963, 18.64, 26.281, 29.215, 28.442, 36.439, 40.425, 39.378, 38.367,
        #                  48.681, 47.281, 46.019, 44.719, 43.538, 42.417, 41.303]

        # harmonic = '17th harmonic'
        # scans_list = [339, 342, 346, 349, 350, 352, 356, 360, 366, 370, 372, 373]
        # ring_currents = [4.5, 9.3, 16.504, 15.229, 14.974, 20.976, 24.866, 30.532, 34.113, 37.123, 35.491, 53.225]

        # harmonic = '18th harmonic'
        # scans_list = [340, 341, 347, 348, 351, 357, 358, 359, 363, 365, 371, 374]
        # ring_currents = [4.4, 9.4, 16.182, 15.732, 21.324, 24.279, 23.767, 31.044, 27.468, 34.721, 36.153, 50.816]


        # # SMI measurements on 04/04/2017:
        x_label = 'dcm_bragg'
        mode = 'bare'
        first = 418
        last = 657
        exclude = [529] + list(range(565, 584))
        scans_list = None
        ring_currents = None

    elif beamline.upper() == 'CHX':
        x_label = 'dcm_b'
        y_label = 'xray_eye1_stats1_total'

        # CHX measurements on 03/18/2017:
        harmonic = '7th harmonic'
        mode = 'reg'

        scans_list = [19041, 19042, 19045, 19046, 19049, 19050, 19053, 19054, 19057]
        ring_currents = [4.84167, 9.44619, 15.18044, 20.93994, 23.91838, 30.37130, 32.92343, 39.49573, 48.11848]

        # harmonic = '11th harmonic'
        # scans_list = [19040, 19043, 19044, 19047, 19048, 19051, 19052, 19055, 19056]
        # ring_currents = [5.04095, 8.93891, 17.08810, 19.20807, 25.97480, 26.80035, 36.00833, 35.39244, 52.94804]
    elif beamline.upper() == 'SRX':
        # SRX measurements on 06/12/2016:
        x_label = 'energy_bragg'
        y_label = 'bpmAD_stats3_total'
        harmonic = '5th harmonic'

        material = ''
        # From https://github.com/NSLS-II-SRX/ipython_ophyd/blob/4716da5d6570f51f0f5b882b627ed57c39c19d34/profile_xf05id1/startup/10-machine.py#L436:
        # cal_data_2016cycle1_2 (2016/1/27 (Se, Cu, Fe, Ti)):
        delta_bragg = 0.315532509387
        d_spacing = 3.12924894907

        mode = 'bare'
        scans_list = ['029c0d3a', '705980d9', '82337021', 'a0d35aba', '54032db3', '7355ac61', '96957282', '83d5c99d',
                      'c727d916']  # bare lattice

        # mode = '1DW'
        # scans_list = ['5519635e', '86e8f4a2', '74cce791', '4a5ba6ca', '6dcfe33a', '4bcb4b69', 'e76cdf48', '0d98ec03',
        #               '295f3c57', 'ab5af66b']  # 1DW
        ring_currents = None

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
        harmonic=harmonic,
        mode=mode,
        delta_bragg=delta_bragg,
        d_spacing=d_spacing,
        **kwargs
    )


def fwhm2espread(fwhm, fitting_coefs=None, mode='reg'):
    allowed_modes = ('reg', 'bare', '1DW')
    assert mode in allowed_modes, '{}: not allowed. Allowed values: {}'.format(mode, allowed_modes)

    # Values from beamlinex/common/fit_data.py (a, b and c coefficients of the quadratic equation):
    a, b, c = fitting_coefs
    espread = a * fwhm ** 2 + b * fwhm + c
    assert espread > 0, '{}: energy spread is negative'.format(espread)
    return espread


if __name__ == '__main__':
    num_bunches = 15

    # beamline = 'SMI'
    # beamline = 'CHX'
    beamline = 'SRX'

    # ***** SMI beamline *****
    # Reg. lattice:

    # 8 pm:
    # lattice = 'reg. lattice'
    # data = np.array([
    #     [24.53058, 0.5],
    #     [32.17943, 0.7],
    #     [39.96556, 0.9],
    #     [47.75136, 1.1],
    #     [55.55569, 1.3],
    #     [63.38812, 1.5],
    # ])

    # 30 pm:
    # lattice = 'reg. lattice'
    # data = np.array([
    #     [24.86341, 0.5],
    #     [32.38799, 0.7],
    #     [40.08822, 0.9],
    #     [47.82172, 1.1],
    #     [55.57577, 1.3],
    #     [63.32070, 1.5],
    # ])

    # 50 pm:
    # lattice = 'reg. lattice'
    # data = np.array([
    #     [25.38570, 0.5],
    #     [32.85911, 0.7],
    #     [40.44787, 0.9],
    #     [48.04519, 1.1],
    #     [55.66512, 1.3],
    #     [63.30655, 1.5],
    # ])

    # Bare lattice:

    # 8 pm:
    lattice = 'bare lattice'
    # lattice = '1DW'
    data = np.array([
        [39.28357, 0.5],
        [45.43406, 0.7],
        [52.22852, 0.9],
        [59.27309, 1.1],
        [66.35909, 1.3],
        [73.47602, 1.5],
    ])

    # 30 pm:
    # lattice = 'bare lattice'
    # lattice = '1DW'
    # data = np.array([
    #     [38.09703, 0.5],
    #     [44.11015, 0.7],
    #     [50.79854, 0.9],
    #     [57.72489, 1.1],
    #     [64.68369, 1.3],
    #     [71.67425, 1.5],
    # ])

    # 50 pm:
    # lattice = 'bare lattice'
    # data = np.array([
    #     [26.39193, 0.5],
    #     [33.82944, 0.7],
    #     [41.35603, 0.9],
    #     [48.88257, 1.1],
    #     [56.48959, 1.3],
    #     [64.17464, 1.5],
    # ])

    # ***** CHX beamline *****
    # Reg. lattice:

    # # 8 pm:
    # lattice = 'reg. lattice'
    # data = np.array([
    #     [31.02236, 0.5],
    #     [39.89320, 0.7],
    #     [48.48306, 0.9],
    #     [57.11007, 1.1],
    #     [65.88523, 1.3],
    #     [74.56814, 1.5],
    # ])

    # # 30 pm:
    # lattice = 'reg. lattice'
    # data = np.array([
    #     [32.64499, 0.5],
    #     [41.18504, 0.7],
    #     [49.70517, 0.9],
    #     [58.26634, 1.1],
    #     [66.89718, 1.3],
    #     [75.41395, 1.5],
    # ])

    # 50 pm:
    # lattice = 'reg. lattice'
    # data = np.array([
    #     [34.40034, 0.5],
    #     [42.79506, 0.7],
    #     [51.43338, 0.9],
    #     [60.01948, 1.1],
    #     [68.23102, 1.3],
    #     [76.63646, 1.5],
    # ])

    x, y, xx2, yy2, fitting_coefs = fit_data(data)
    x_label = 'FWHM ({}) [eV]'.format(lattice)
    y_label = r'Energy spread, 10$^{-3}$'
    title = 'Energy spread vs. FWHM ({})'.format(lattice)
    file_name = '{}.png'.format(title.replace(' ', '_'))

    plot_data(x, y, xx2, yy2, fitting_coefs, x_label, y_label, title=title, file_name=file_name)

    main(beamline=beamline, fitting_coefs=fitting_coefs, num_bunches=num_bunches)
