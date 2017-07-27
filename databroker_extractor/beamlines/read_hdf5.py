import os

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from chxanalys.chx_libs import cmap_albula
from chxanalys.chx_packages import load_mask
from matplotlib.colors import LogNorm

from databroker_extractor.beamlines.eiger_images import save_hdf5
from databroker_extractor.common.plot import clear_plt


def plot_1d(data, hdf5_files, figsize=(12, 9), img_name='img.png', dpi=400, log=False, show=False):
    # Plot the cuts
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    for k, v in data.items():
        if log:
            v = np.log10(v)
        ax.plot(v, label='{} ({})'.format(hdf5_files[k], os.path.splitext(k)[0]))
    plt.legend()
    plt.savefig(img_name, dpi=dpi)
    if show:
        plt.show()
    clear_plt()


if __name__ == '__main__':
    data_dir = 'C:\\Users\\mraki\\Documents\\Work\\Beamlines\\CHX\\2017-07-12 CHX eiger data\\'
    hdf5_files = {
        '201706262217_101631_2849.h5': '0.03 mm',
        '201706262206_69c533_2847.h5': '0.05 mm',
        '201706262157_541142_2845.h5': '0.1 mm',
        '201706262225_3dbf3e_2851.h5': '0.2 mm',
    }
    # Masks:
    # mask = load_mask(data_dir, 'June26_chubar.npy', reverse=True)
    mask = load_mask(data_dir, 'June26_chubar_diffraction.npy', reverse=True)
    chip_mask = np.load(os.path.join(data_dir, 'Eiger4M_chip_mask.npy'))

    y_center = 925

    slices = {}
    # img_num = 0
    # img_num = 10
    # img_num = 100
    img_num = 'mean'

    # rotate = True
    rotate = False
    rotate_angle = -30

    # cmap = 'gray'
    cmap = cmap_albula

    for hdf5_file, desc in hdf5_files.items():
        hdf5_file_full = os.path.join(data_dir, hdf5_file)
        fig_file_basename = '{}_img_{}'.format(os.path.splitext(hdf5_file_full)[0], img_num)
        fig_file = '{}.png'.format(fig_file_basename)
        hdf5_save_file = '{}.h5'.format(fig_file_basename)
        f = h5py.File(hdf5_file_full, 'r')
        data = f['dataset']

        d = (data[img_num] if img_num is not 'mean' else np.mean(data, axis=0)) * mask * chip_mask

        if rotate:
            rotated_data = scipy.ndimage.interpolation.rotate(d, angle=rotate_angle, reshape=False, order=0)
            where_negative = np.where(rotated_data < 0)
            print('where_negative:', where_negative)
            rotated_data[where_negative] = 0
        else:
            rotated_data = d

        # Save data to HDF5 for further import to Igor Pro:
        status = save_hdf5(rotated_data, filename=hdf5_save_file)
        print('Status: {} for file {}'.format(status, hdf5_save_file))

        fig, ax = plt.subplots(figsize=(8, 6))
        pos = ax.imshow(rotated_data, norm=LogNorm(), vmin=1e-4, vmax=1e4, cmap=cmap, aspect='equal',
                        interpolation='none')
        fig.colorbar(pos, ax=ax)
        if rotate:
            plt.axhline(y_center, color='red')
        plt.title(desc)
        plt.savefig(fig_file, dpi=200)
        clear_plt()

        slices[hdf5_file] = rotated_data[y_center, :]

    # Plot the cut in linear scale:
    slices_basename = os.path.join(data_dir, 'slices_img_{}'.format(img_num))
    plot_1d(slices, hdf5_files, img_name='{}.png'.format(slices_basename))

    # Plot the cut in log scale:
    slices_basename_log = os.path.join(data_dir, 'slices_img_{}_log'.format(img_num))
    plot_1d(slices, hdf5_files, img_name='{}.png'.format(slices_basename_log), log=True)

    # Pandas dataframe with the cuts:
    columns = []
    data = []
    for k, v in slices.items():
        colname = 'CHX_{}_{}_{}'.format(
            hdf5_files[k].replace(' ', ''),
            k.split('_')[1],
            img_num,
        )
        columns.append(colname)
        data.append(v)
    data = pd.DataFrame(np.array(data).T, columns=columns)
    data.to_csv('{}.csv'.format(slices_basename), index=None)
    with open('{}.dat'.format(slices_basename), 'w') as f:
        f.write(data.to_string(columns=columns))

    print('')
