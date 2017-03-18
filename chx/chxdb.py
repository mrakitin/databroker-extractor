# -*- coding: utf-8 -*-
"""
This is a library for experimental data processing from the CHX beamline of NSLS-II. It requires the SRW utils library,
please download https://github.com/ochubar/SRW/blob/master/env/work/srw_python/uti_math.py#L615 and add it to your
PYTHONPATH environment variable.
"""

import datetime
import time

import numpy as np
from PIL import Image
from databroker import db, get_fields, get_images, get_table
from matplotlib import pyplot as plt


def fwhm(x, y):  # MR27092016
    """The function searches x-values (roots) where y=0 based on linear interpolation, and calculates FWHM"""

    def is_positive(num):
        return True if num > 0 else False

    positive = is_positive(y[0])
    list_of_roots = []
    for i in range(len(y)):
        current_positive = is_positive(y[i])
        if current_positive != positive:
            list_of_roots.append(x[i - 1] + (x[i] - x[i - 1]) / (abs(y[i]) + abs(y[i - 1])) * abs(y[i - 1]))
            positive = not positive
    if len(list_of_roots) >= 2:
        return abs(list_of_roots[-1] - list_of_roots[0])
    else:
        raise Exception('Number of roots is less than 2!')


def get_and_plot(scan_id, save=False, field='', idx=None):
    """Get data from table and plot it (produces Intensity vs. Ugap or mono angle).

    :param scan_id: scan id from bluesky.
    :param save: an option to save a picture instead of showing it.
    :param field: visualize the intensity vs. this field.
    :param idx: index of the image (used as a part of the name in the saving process).
    :return: None.
    """
    g, e, t = get_data(scan_id, field=field)
    plot_scan(g, e, scan_id=scan_id, timestamp=t, save=save, field=field, idx=idx)


def get_data(scan_id, field='ivu_gap', intensity_field='elm_sum_all', det=None, debug=False):
    """Get data from the scan stored in the table.

    :param scan_id: scan id from bluesky.
    :param field: visualize the intensity vs. this field.
    :param intensity_field: the name of the intensity field.
    :param det: the name of the detector.
    :param debug: a debug flag.
    :return: a tuple of X, Y and timestamp values.
    """
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
    x = table[field]
    y = table[intensity_field]

    return x, y, t


def get_scan(scan_id, debug=False):
    """Get scan from databroker using provided scan id.

    :param scan_id: scan id from bluesky.
    :param debug: a debug flag.
    :return: a tuple of scan and timestamp values.
    """
    scan = db[scan_id]
    t = datetime.datetime.fromtimestamp(scan['start']['time']).strftime('%Y-%m-%d %H:%M:%S')
    if debug:
        print(scan)
    print('Scan ID: {}  Timestamp: {}'.format(scan_id, t))
    return scan, t


def get_scans_list(keyword):
    """Get a list of scan filtered by the provided keyword.

    :param keyword: a keyword to search scans.
    :return: a list of found scans.
    """
    return db(keyword)


def plot_scan(x, y, scan_id, timestamp, save, field, idx):
    """Plot intensities vs. scan variable.

    :param x: scan variable.
    :param y: intensity.
    :param scan_id: scan id from bluesky.
    :param timestamp: a timestamp of the scan.
    :param save: a flag to save the produced image.
    :param field: visualize the intensity vs. this field.
    :param idx: index of the image (used as a part of the name in the saving process).
    :return: None.
    """
    x = np.array(x)
    y = np.array(y)
    if field == 'ivu_gap':
        units = 'mm'
    elif field == 'dcm_b':
        units = 'deg'
    else:
        raise ValueError('Unknown field: {}'.format(field))
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
    xlabel = field.replace('_', ' ')

    ax.set_xlabel('{} [{}]'.format(xlabel, units))
    ax.set_ylabel('Intensity [arb. units]')
    if not save:
        plt.show()
    else:
        if idx is not None:
            plt.savefig('scan_{:02d}_{}.png'.format(idx, scan_id))
        else:
            plt.savefig('scan_{}.png'.format(scan_id))


def save_dat_file(data, name, header=None):
    kwargs = {}
    if header:
        kwargs['header'] = header
    np.savetxt(
        name,
        data,
        **kwargs
    )


def save_raw_image(data, name):
    im = Image.fromarray(data).convert('L')
    im.save(name)


def _clear_plt():
    """Clear the plots (useful when plotting in a loop).

    :return: None
    """
    plt.cla()
    plt.clf()
    plt.close()


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
    detector = 'xray_eye3_image'

    harmonics_scan = True
    fiber_scan = False
    pinhole_scan = False
    list_scans = False

    clim = (0, 255)
    cmap = 'jet'
    plt.rcParams['image.cmap'] = cmap
    enable_log_correction = False

    if harmonics_scan:
        # Harmonics scan:
        scan_ids = [
            # center vertical mbs on ID cone: 0.6x1.2 (pbs) 17585 (scan#) date: 02/28/2017
            # ID harmonic: 5th energy: 9.65keV gap: 6.640
            # Ti foil, elm: 50pC, .1s .05x.05,.1x.4
            #     100pC, .1s .2x.4
            # ('1eff511d', 'ivu_gap'),
            # ('8f6a6004', 'ivu_gap'),
            # ('1f1422b4', 'ivu_gap'),
            # ('7949f1b0', 'dcm_b'),
            # ('daeb15e3', 'dcm_b'),
            # ('6edfa33a', 'dcm_b'),
            # center vertical mbs on ID cone: 0.6x1.2 (pbs) .4x.1 (mbs)  17599 (scan#)
            # ID harmonic: 7th energy: 9.75keV gap: 5.240 can't scan gap at 9.65keV...
            # Ti foil, elm: 50pC, .1s .05x.05,.1x.4
            #     100pC, .1s .2x.4
            # ('74798cb6', 'ivu_gap'),
            # ('dc2b5045', 'ivu_gap'),
            # ('c4f95268', 'ivu_gap'),
            # ('b2365717', 'dcm_b'),
            # ('ac99ddd0', 'dcm_b'),
            # ('b808a890', 'dcm_b'),
            # center vertical mbs on ID cone: 0.6x1.2 (pbs) .4x.1 (mbs) 17610 (scan#)
            # gap scan: #17613
            # ID harmonic: 7th energy: 9.65keV gap: 5.2017
            # Ti foil, elm: 50pC, .1s .05x.05,.1x.4
            #     100pC, .1s .2x.4
            # ('e23fb7a1', 'dcm_b'),
            # ('afc6da9e', 'dcm_b'),
            # ('e71b8b5f', 'dcm_b'),
            # 2017-03-18 (elevation studies):
            ('809d548e', 'dcm_b'),
        ]

        save = True
        # save = False

        for i, scan_id in enumerate(scan_ids):
            get_and_plot(scan_id[0], save=save, field=scan_id[1], idx=i)

    if fiber_scan:
        first_slice = 1000
        second_slice = 1250
        third_slice = 1500

        # Dark field:
        scan_id_dark_field = '12738c63'
        scan_dark_field, t_dark_field = get_scan(scan_id_dark_field)
        images_dark_field = get_images(scan_dark_field, detector)
        mean_dark_field = np.mean(images_dark_field[0], axis=0)
        print('     ID: {}  Number of images: {}'.format(scan_id_dark_field, len(images_dark_field[0])))
        print('     Min: {}  Max: {}\n'.format(mean_dark_field.min(), mean_dark_field.max()))

        plt.imshow(mean_dark_field, clim=clim, cmap=cmap)
        plt.savefig('mean_dark_field_{}.png'.format(scan_id_dark_field))
        _clear_plt()

        shape = mean_dark_field.shape
        print('Shape of mean_dark_field: {}'.format(shape))

        save_dat_file(data=mean_dark_field, name='mean_dark_field_{}.dat'.format(scan_id_dark_field))
        save_raw_image(data=mean_dark_field, name='mean_dark_field_{}.tif'.format(scan_id_dark_field))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim((0, shape[0]))
        ax.grid()
        ax.plot(mean_dark_field[:, first_slice], label='pixel={}'.format(first_slice))
        ax.plot(mean_dark_field[:, second_slice], label='pixel={}'.format(second_slice))
        ax.plot(mean_dark_field[:, third_slice], label='pixel={}'.format(third_slice))
        ax.legend()
        fig.savefig('mean_dark_field_slices_{}.png'.format(scan_id_dark_field))
        _clear_plt()

        # Fiber in:
        scan_id_fiber_in = '58732824'
        scan_fiber_in, t_fiber_in = get_scan(scan_id_fiber_in)
        images_fiber_in = get_images(scan_fiber_in, detector)
        mean_fiber_in = np.mean(images_fiber_in[0], axis=0)
        print('     ID: {}  Number of images: {}'.format(scan_id_fiber_in, len(images_fiber_in[0])))
        print('     Min: {}  Max: {}\n'.format(mean_fiber_in.min(), mean_fiber_in.max()))

        plt.imshow(mean_fiber_in, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_in_{}.png'.format(scan_id_fiber_in))
        _clear_plt()

        # Fiber out:
        scan_id_fiber_out = '190ae619'
        scan_fiber_out, t_fiber_out = get_scan(scan_id_fiber_out)
        images_fiber_out = get_images(scan_fiber_out, detector)
        mean_fiber_out = np.mean(images_fiber_out[0], axis=0)
        print('     ID: {}  Number of images: {}'.format(scan_id_fiber_out, len(images_fiber_out[0])))
        print('     Min: {}  Max: {}\n'.format(mean_fiber_out.min(), mean_fiber_out.max()))

        plt.imshow(mean_fiber_out, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_out_{}.png'.format(scan_id_fiber_out))
        _clear_plt()

        # Diff fiber in and dark field:
        mean_diff_fiber_in = mean_fiber_in - mean_dark_field
        print('Min: {}  Max: {}\n'.format(mean_diff_fiber_in.min(), mean_diff_fiber_in.max()))
        plt.imshow(mean_diff_fiber_in, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_in_minus_mean_dark_field.png')
        _clear_plt()

        shape = mean_diff_fiber_in.shape
        print('Shape of mean_diff_fiber_in: {}'.format(shape))

        save_dat_file(data=mean_diff_fiber_in, name='mean_fiber_in_minus_mean_dark_field.dat')
        save_raw_image(data=mean_diff_fiber_in, name='mean_fiber_in_minus_mean_dark_field.tif')

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim((0, shape[0]))
        ax.grid()
        ax.plot(mean_diff_fiber_in[:, first_slice], label='pixel={}'.format(first_slice))
        ax.plot(mean_diff_fiber_in[:, second_slice], label='pixel={}'.format(second_slice))
        ax.plot(mean_diff_fiber_in[:, third_slice], label='pixel={}'.format(third_slice))
        ax.legend()
        fig.savefig('mean_fiber_in_minus_mean_dark_field_slices.png')
        _clear_plt()

        # Diff fiber in and dark field:
        mean_diff_fiber_out = mean_fiber_out - mean_dark_field
        print('Min: {}  Max: {}\n'.format(mean_diff_fiber_out.min(), mean_diff_fiber_out.max()))
        plt.imshow(mean_diff_fiber_out, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_out_minus_mean_dark_field.png')
        _clear_plt()

        shape = mean_diff_fiber_out.shape
        print('Shape of mean_diff_fiber_out: {}'.format(shape))

        save_dat_file(data=mean_diff_fiber_out, name='mean_fiber_out_minus_mean_dark_field.dat')
        save_raw_image(data=mean_diff_fiber_out, name='mean_fiber_out_minus_mean_dark_field.tif')

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim((0, shape[0]))
        ax.grid()
        ax.plot(mean_diff_fiber_out[:, first_slice], label='pixel={}'.format(first_slice))
        ax.plot(mean_diff_fiber_out[:, second_slice], label='pixel={}'.format(second_slice))
        ax.plot(mean_diff_fiber_out[:, third_slice], label='pixel={}'.format(third_slice))
        ax.legend()
        fig.savefig('mean_fiber_out_minus_mean_dark_field_slices.png')
        _clear_plt()

        # Fiber in - fiber out:
        mean_fiber_in_minus_out = mean_diff_fiber_in - mean_diff_fiber_out
        print('Min: {}  Max: {}\n'.format(mean_fiber_in_minus_out.min(), mean_fiber_in_minus_out.max()))
        plt.imshow(mean_fiber_in_minus_out, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_in_minus_out.png')
        _clear_plt()

        # Fiber in / fiber out:
        where_zero = np.where(mean_diff_fiber_out == 0)
        mean_diff_fiber_out[where_zero] = 1
        mean_fiber_in_div_out = mean_diff_fiber_in / mean_diff_fiber_out
        print('Min: {}  Max: {}\n'.format(mean_fiber_in_div_out.min(), mean_fiber_in_div_out.max()))
        max_in = mean_diff_fiber_in.max()
        max_out = mean_diff_fiber_out.max()
        print('Max in: {}  Max out: {}'.format(max_in, max_out))
        plt.imshow(mean_fiber_in_div_out, clim=max_in / max_out, cmap=cmap)
        plt.savefig('mean_fiber_in_div_out.png')
        _clear_plt()

    if pinhole_scan:
        # Dark field:
        start_time = time.time()

        scan_id_dark_field = 'a9a0687c'
        scan_dark_field, t_dark_field = get_scan(scan_id_dark_field)
        images_dark_field = get_images(scan_dark_field, detector)
        mean_dark_field = np.mean(images_dark_field[0], axis=0)

        # Left and right parts have different chips, so need to normalize left and right parts:
        '''
        np.mean(mean_dark_field[:, :mean_dark_field.shape[1]/2])
        Out[7]: 2.1016548665364585

        In [8]: np.mean(mean_dark_field[:, mean_dark_field.shape[1]/2:])
        Out[8]: 2.8157670403773496
        '''

        '''
        left_mean = np.mean(mean_dark_field[:, :mean_dark_field.shape[1] / 2])
        right_mean = np.mean(mean_dark_field[:, mean_dark_field.shape[1] / 2:])
        if left_mean > right_mean:
            mean_dark_field[:, mean_dark_field.shape[1] / 2:] = mean_dark_field[:,
                                                                mean_dark_field.shape[1] / 2:] * left_mean / right_mean
        else:
            mean_dark_field[:, :mean_dark_field.shape[1] / 2] = mean_dark_field[:,
                                                                :mean_dark_field.shape[1] / 2] * right_mean / left_mean
        '''
        log_mean_dark_field = np.log10(mean_dark_field)
        if enable_log_correction:
            neg_idx = np.where(log_mean_dark_field <= 0)
            log_mean_dark_field[neg_idx] = 0.0
        print('     ID: {}  Number of images: {}'.format(scan_id_dark_field, len(images_dark_field[0])))
        print('     Min: {}  Max: {}'.format(mean_dark_field.min(), mean_dark_field.max()))

        plt.imshow(mean_dark_field, clim=clim, cmap=cmap)
        # plt.imshow(log_mean_dark_field, cmap=cmap)
        plt.savefig('mean_pinhole_dark_field_{}.png'.format(scan_id_dark_field))
        _clear_plt()

        # plt.imshow(mean_dark_field, clim=clim, cmap=cmap)
        plt.imshow(log_mean_dark_field, cmap=cmap)
        plt.savefig('mean_pinhole_dark_field_{}_log.png'.format(scan_id_dark_field))
        _clear_plt()

        print('Duration: {:.3f} sec\n'.format(time.time() - start_time))

        # Pinhole:
        start_time = time.time()

        scan_id_pinhole = 'afe3cf59'
        scan_pinhole, t_pinhole = get_scan(scan_id_pinhole)
        images_pinhole = get_images(scan_pinhole, detector)
        mean_pinhole = np.mean(images_pinhole[0], axis=0)
        mean_pinhole_orig = np.copy(mean_pinhole)
        mean_pinhole /= mean_dark_field

        '''
        if left_mean > right_mean:
            mean_pinhole[:, mean_pinhole.shape[1] / 2:] = mean_pinhole[:,
                                                          mean_pinhole.shape[1] / 2:] * left_mean / right_mean
        else:
            mean_pinhole[:, :mean_pinhole.shape[1] / 2] = mean_pinhole[:,
                                                          :mean_pinhole.shape[1] / 2] * right_mean / left_mean
        '''
        log_mean_pinhole = np.log10(mean_pinhole)
        if enable_log_correction:
            neg_idx = np.where(log_mean_pinhole <= 0)
            log_mean_pinhole[neg_idx] = 0.0
        print('     ID: {}  Number of images: {}'.format(scan_id_pinhole, len(images_pinhole[0])))
        print('     Min: {}  Max: {}'.format(mean_pinhole.min(), mean_pinhole.max()))

        plt.imshow(mean_pinhole, clim=clim, cmap=cmap)
        # plt.imshow(log_mean_pinhole, cmap=cmap)
        plt.savefig('mean_pinhole_{}.png'.format(scan_id_pinhole))
        _clear_plt()

        # plt.imshow(mean_pinhole, clim=clim, cmap=cmap)
        plt.imshow(log_mean_pinhole, cmap=cmap)
        plt.savefig('mean_pinhole_{}_log.png'.format(scan_id_pinhole))
        _clear_plt()

        plt.imshow(mean_pinhole_orig, clim=clim, cmap=cmap)
        plt.savefig('mean_pinhole_{}_orig.png'.format(scan_id_pinhole))
        _clear_plt()

        plt.imshow(np.log10(mean_pinhole_orig), cmap=cmap)
        plt.savefig('mean_pinhole_{}_orig_log.png'.format(scan_id_pinhole))
        _clear_plt()

        print('Duration: {:.3f} sec\n'.format(time.time() - start_time))

        # # Diff pinhole and dark field:
        # # mean_diff_pinhole = mean_pinhole - mean_dark_field
        # mean_diff_pinhole = mean_pinhole
        # log_mean_diff_pinhole = np.log10(mean_diff_pinhole)
        # if enable_log_correction:
        #     neg_idx = np.where(log_mean_diff_pinhole <= 0)
        #     log_mean_diff_pinhole[neg_idx] = 0.0
        # print('Min: {}  Max: {}\n'.format(log_mean_diff_pinhole.min(), log_mean_diff_pinhole.max()))
        # # plt.imshow(mean_diff_pinhole, clim=clim, cmap=cmap)
        # plt.imshow(log_mean_diff_pinhole, cmap=cmap)
        # plt.savefig('mean_pinhole_minus_mean_dark_field_log.png')
        # _clear_plt()

    if list_scans:
        scans_list = get_scans_list(keyword='Chubar')
        print('Scans list: {}'.format(len(scans_list)))
        for s in scans_list:
            print(s)

    print('Done')
