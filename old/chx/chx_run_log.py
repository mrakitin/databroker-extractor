import databroker as db
import numpy as np
from matplotlib import pyplot as plt

from databroker_extractor import common as c_db, common as c_dt, common as c_io, common as c_plot

if __name__ == '__main__':
    detector = 'xray_eye3_image'

    # This may be used if the configuration is not set via ~/.config. See the following documentation for more details:
    # http://nsls-ii.github.io/databroker/configuration.html
    '''
    from metadatastore.mds import MDSRO  # metadata store read-only
    from filestore.fs import FileStoreRO  # file store read-only
    from databroker import db # Broker, DataBroker as db, get_images, get_table, get_events, get_fields

    # This an example. You'll need to know your local configuration.
    mds = MDSRO({'host': 'localhost',
                 'port': 27018,
                 'database': 'datastore',
                 'timezone': 'US/Eastern'})

    # This an example. You'll need to know your local configuration.
    fs = FileStoreRO(
        config={
            'host': 'localhost',
            'port': 27018,
            'database': 'filestore',
        },
        root_map={'/': 'W:'}
    )

    import filestore.api as fsapi
    from filestore.handlers import NpyHandler, SingleTiffHandler, AreaDetectorTiffHandler
    # fsapi.register_handler('tiff', SingleTiffHandler)
    fsapi.register_handler('tiff', AreaDetectorTiffHandler)

    db = Broker(mds, fs)
    db.get_images(db['58732824'], detector)
    '''
    # db.DataBroker.fs.root_map = {'/': 'W:\\'}
    # scan_id = -1
    # scan_id = '31a8fc'

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

        # save = True
        save = False

        for i, scan_id in enumerate(scan_ids):
            chx.get_and_plot(scan_id[0], save=save, field=scan_id[1], idx=i, is_vs_energy=True)

    if fiber_scan:
        first_slice = 1000
        second_slice = 1250
        third_slice = 1500

        # Dark field:
        scan_id_dark_field = '12738c63'
        scan_dark_field, t_dark_field = c_db.get_scan(scan_id_dark_field)
        images_dark_field = db.get_images(scan_dark_field, detector)
        mean_dark_field = np.mean(images_dark_field[0], axis=0)
        print('     ID: {}  Number of images: {}'.format(scan_id_dark_field, len(images_dark_field[0])))
        print('     Min: {}  Max: {}\n'.format(mean_dark_field.min(), mean_dark_field.max()))

        plt.imshow(mean_dark_field, clim=clim, cmap=cmap)
        plt.savefig('mean_dark_field_{}.png'.format(scan_id_dark_field))
        c_plot.clear_plt()

        shape = mean_dark_field.shape
        print('Shape of mean_dark_field: {}'.format(shape))

        c_io.save_data_numpy(data=mean_dark_field, name='mean_dark_field_{}.dat'.format(scan_id_dark_field))
        c_plot.save_raw_image(data=mean_dark_field, name='mean_dark_field_{}.tif'.format(scan_id_dark_field))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim((0, shape[0]))
        ax.grid()
        ax.plot(mean_dark_field[:, first_slice], label='pixel={}'.format(first_slice))
        ax.plot(mean_dark_field[:, second_slice], label='pixel={}'.format(second_slice))
        ax.plot(mean_dark_field[:, third_slice], label='pixel={}'.format(third_slice))
        ax.legend()
        fig.savefig('mean_dark_field_slices_{}.png'.format(scan_id_dark_field))
        c_plot.clear_plt()

        # Fiber in:
        scan_id_fiber_in = '58732824'
        scan_fiber_in, t_fiber_in = c_db.get_scan(scan_id_fiber_in)
        images_fiber_in = db.get_images(scan_fiber_in, detector)
        mean_fiber_in = np.mean(images_fiber_in[0], axis=0)
        print('     ID: {}  Number of images: {}'.format(scan_id_fiber_in, len(images_fiber_in[0])))
        print('     Min: {}  Max: {}\n'.format(mean_fiber_in.min(), mean_fiber_in.max()))

        plt.imshow(mean_fiber_in, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_in_{}.png'.format(scan_id_fiber_in))
        c_plot.clear_plt()

        # Fiber out:
        scan_id_fiber_out = '190ae619'
        scan_fiber_out, t_fiber_out = c_db.get_scan(scan_id_fiber_out)
        images_fiber_out = db.get_images(scan_fiber_out, detector)
        mean_fiber_out = np.mean(images_fiber_out[0], axis=0)
        print('     ID: {}  Number of images: {}'.format(scan_id_fiber_out, len(images_fiber_out[0])))
        print('     Min: {}  Max: {}\n'.format(mean_fiber_out.min(), mean_fiber_out.max()))

        plt.imshow(mean_fiber_out, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_out_{}.png'.format(scan_id_fiber_out))
        c_plot.clear_plt()

        # Diff fiber in and dark field:
        mean_diff_fiber_in = mean_fiber_in - mean_dark_field
        print('Min: {}  Max: {}\n'.format(mean_diff_fiber_in.min(), mean_diff_fiber_in.max()))
        plt.imshow(mean_diff_fiber_in, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_in_minus_mean_dark_field.png')
        c_plot.clear_plt()

        shape = mean_diff_fiber_in.shape
        print('Shape of mean_diff_fiber_in: {}'.format(shape))

        c_io.save_data_numpy(data=mean_diff_fiber_in, name='mean_fiber_in_minus_mean_dark_field.dat')
        c_plot.save_raw_image(data=mean_diff_fiber_in, name='mean_fiber_in_minus_mean_dark_field.tif')

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim((0, shape[0]))
        ax.grid()
        ax.plot(mean_diff_fiber_in[:, first_slice], label='pixel={}'.format(first_slice))
        ax.plot(mean_diff_fiber_in[:, second_slice], label='pixel={}'.format(second_slice))
        ax.plot(mean_diff_fiber_in[:, third_slice], label='pixel={}'.format(third_slice))
        ax.legend()
        fig.savefig('mean_fiber_in_minus_mean_dark_field_slices.png')
        c_plot.clear_plt()

        # Diff fiber in and dark field:
        mean_diff_fiber_out = mean_fiber_out - mean_dark_field
        print('Min: {}  Max: {}\n'.format(mean_diff_fiber_out.min(), mean_diff_fiber_out.max()))
        plt.imshow(mean_diff_fiber_out, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_out_minus_mean_dark_field.png')
        c_plot.clear_plt()

        shape = mean_diff_fiber_out.shape
        print('Shape of mean_diff_fiber_out: {}'.format(shape))

        c_io.save_data_numpy(data=mean_diff_fiber_out, name='mean_fiber_out_minus_mean_dark_field.dat')
        c_plot.save_raw_image(data=mean_diff_fiber_out, name='mean_fiber_out_minus_mean_dark_field.tif')

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim((0, shape[0]))
        ax.grid()
        ax.plot(mean_diff_fiber_out[:, first_slice], label='pixel={}'.format(first_slice))
        ax.plot(mean_diff_fiber_out[:, second_slice], label='pixel={}'.format(second_slice))
        ax.plot(mean_diff_fiber_out[:, third_slice], label='pixel={}'.format(third_slice))
        ax.legend()
        fig.savefig('mean_fiber_out_minus_mean_dark_field_slices.png')
        c_plot.clear_plt()

        # Fiber in - fiber out:
        mean_fiber_in_minus_out = mean_diff_fiber_in - mean_diff_fiber_out
        print('Min: {}  Max: {}\n'.format(mean_fiber_in_minus_out.min(), mean_fiber_in_minus_out.max()))
        plt.imshow(mean_fiber_in_minus_out, clim=clim, cmap=cmap)
        plt.savefig('mean_fiber_in_minus_out.png')
        c_plot.clear_plt()

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
        c_plot.clear_plt()

    if pinhole_scan:
        # Dark field:
        start_time = c_dt.current_timestamp()

        scan_id_dark_field = 'a9a0687c'
        scan_dark_field, t_dark_field = c_db.get_scan(scan_id_dark_field)
        images_dark_field = db.get_images(scan_dark_field, detector)
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
        c_plot.clear_plt()

        # plt.imshow(mean_dark_field, clim=clim, cmap=cmap)
        plt.imshow(log_mean_dark_field, cmap=cmap)
        plt.savefig('mean_pinhole_dark_field_{}_log.png'.format(scan_id_dark_field))
        c_plot.clear_plt()

        print('Duration: {:.3f} sec\n'.format(c_dt.current_timestamp() - start_time))

        # Pinhole:
        start_time = c_dt.current_timestamp()

        scan_id_pinhole = 'afe3cf59'
        scan_pinhole, t_pinhole = c_db.get_scan(scan_id_pinhole)
        images_pinhole = db.get_images(scan_pinhole, detector)
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
        c_plot.clear_plt()

        # plt.imshow(mean_pinhole, clim=clim, cmap=cmap)
        plt.imshow(log_mean_pinhole, cmap=cmap)
        plt.savefig('mean_pinhole_{}_log.png'.format(scan_id_pinhole))
        c_plot.clear_plt()

        plt.imshow(mean_pinhole_orig, clim=clim, cmap=cmap)
        plt.savefig('mean_pinhole_{}_orig.png'.format(scan_id_pinhole))
        c_plot.clear_plt()

        plt.imshow(np.log10(mean_pinhole_orig), cmap=cmap)
        plt.savefig('mean_pinhole_{}_orig_log.png'.format(scan_id_pinhole))
        c_plot.clear_plt()

        print('Duration: {:.3f} sec\n'.format(c_dt.current_timestamp() - start_time))

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
        scans_list = c_db.get_scans_list(keyword='Chubar')
        print('Scans list: {}'.format(len(scans_list)))
        for s in scans_list:
            print(s)

    print('Done')
