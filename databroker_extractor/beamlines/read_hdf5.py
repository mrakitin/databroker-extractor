import os

import h5py
import matplotlib.pyplot as plt
import numpy as np
import scipy
from chxanalys.chx_libs import cmap_albula
from chxanalys.chx_packages import load_mask
from matplotlib.colors import LogNorm

from databroker_extractor.common.plot import clear_plt

if __name__ == '__main__':
    data_dir = 'C:\\Users\\mraki\\Documents\\Work\\Beamlines\\CHX\\2017-07-12 CHX eiger data\\'
    hdf5_files = {
        '201706262217_101631_2849.h5': '0.03 mm',
        '201706262206_69c533_2847.h5': '0.05 mm',
        '201706262157_541142_2845.h5': '0.1 mm',
        '201706262225_3dbf3e_2851.h5': '0.2 mm',
    }
    # Masks:
    mask = load_mask(data_dir, 'June26_chubar.npy', reverse=True)
    chip_mask = np.load(os.path.join(data_dir, 'Eiger4M_chip_mask.npy'))

    y_center = 925

    slices = {}
    # img_num = 0
    # img_num = 100
    img_num = 'mean'

    rotate = True
    # cmap = 'gray'
    cmap = cmap_albula
    for hdf5_file, desc in hdf5_files.items():
        hdf5_file_full = os.path.join(data_dir, hdf5_file)
        fig_file = '{}_img_{}.png'.format(os.path.splitext(hdf5_file_full)[0], img_num)
        f = h5py.File(hdf5_file_full, 'r')
        data = f['dataset']

        d = (data[img_num] if img_num is not 'mean' else np.mean(data, axis=0)) * mask * chip_mask

        if rotate:
            rotated_data = scipy.ndimage.interpolation.rotate(d, angle=-30, reshape=False, order=0)
            where_negative = np.where(rotated_data < 0)
            print('where_negative:', where_negative)
            rotated_data[where_negative] = 0
        else:
            rotated_data = d

        fig, ax = plt.subplots(figsize=(8, 6))
        pos = ax.imshow(rotated_data, norm=LogNorm(), vmin=1e-4, vmax=1e4, cmap=cmap, aspect='equal',
                        interpolation='none')
        fig.colorbar(pos, ax=ax)
        plt.axhline(y_center, color='red')
        plt.title(desc)
        plt.savefig(fig_file, dpi=200)
        clear_plt()

        slices[hdf5_file] = rotated_data[y_center, :]

    # Plot the cut in linear scale:
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)
    for k, v in slices.items():
        ax.plot(v, label='{} ({})'.format(hdf5_files[k], os.path.splitext(k)[0]))
    plt.legend()
    plt.savefig(os.path.join(data_dir, 'slices_img_{}.png'.format(img_num)), dpi=400)

    # Plot the cut in log scale:
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)
    for k, v in slices.items():
        ax.plot(np.log10(v), label='{} ({})'.format(hdf5_files[k], os.path.splitext(k)[0]))
    plt.legend()
    plt.savefig(os.path.join(data_dir, 'slices_img_{}_log.png'.format(img_num)), dpi=400)

    # Pandas dataframe with the cuts:



    print('')
