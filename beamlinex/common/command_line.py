#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import json
import os


def get_beamline_labels(config_dict, label):
    allowed_labels = ('x_label', 'y_label')
    assert label.lower() in allowed_labels, '{}: label not allowed. Allowed values: {}'.format(label, allowed_labels)
    return config_dict['default_labels'][label]


def get_beamline_units(config_dict, units):
    allowed_labels = ('x_units', 'y_units')
    assert units.lower() in allowed_labels, '{}: units not allowed. Allowed values: {}'.format(units, allowed_labels)
    return config_dict['default_labels'][units]


def parse_command_line():
    # Plot a single graph:
    parser = argparse.ArgumentParser(description='Accessing and visualizing data from NSLS-II beamlines')

    # Select a beamline:
    parser.add_argument('-b', '--beamline', dest='beamline', default=None, choices=('chx', 'CHX', 'smi', 'SMI'),
                        help='select beamline to get data from')

    # Plot data:
    parser.add_argument('-p', '--plot-ids', dest='plot_ids', default=None, nargs='*',
                        help='plot data for blank-separated scan ids list')
    parser.add_argument('-n', '--norm-plots', dest='norm_plots', default=None, choices=('total', 'individual'),
                        help='normalize plots')
    parser.add_argument('-x', '--x-label', dest='x_label', default=None, help='x label to plot')
    parser.add_argument('-y', '--y-label', dest='y_label', default=None, help='y label to plot')
    parser.add_argument('--x-units', dest='x_units', default=None, help='x units')
    parser.add_argument('--y-units', dest='y_units', default=None, help='y units')
    parser.add_argument('--scatter-size', dest='scatter_size', default=None, help='scatter size')
    parser.add_argument('-e', '--convert-to-energy', dest='convert_to_energy', action='store_true',
                        help='convert to energy from Bragg diffraction angle')

    # Save data:
    parser.add_argument('-s', '--save-ids', dest='save_ids', default=None, nargs='*',
                        help='save data for blank-separated scan ids list')
    parser.add_argument('-r', '--range', dest='range_ids', default=None,
                        help='save data for a range of scan ids list')
    parser.add_argument('-c', '--columns', dest='columns', default=None, nargs='+',
                        help='columns to save to a file')
    parser.add_argument('-i', '--hide-index-column', dest='hide_index_column', action='store_false',
                        help='hide index column in the saved file(s)')

    # File name variables:
    parser.add_argument('-t', '--timestamp', dest='timestamp', default=None, choices=('scan', 'current'),
                        help='add scan (or current) timestamp to the name of the saved file')
    parser.add_argument('-d', '--data-extension', dest='data_extension', default='dat',
                        help='extension of the saved file')
    parser.add_argument('-g', '--graph-extension', dest='graph_extension', default='png',
                        help='extension of the saved graph')

    args = parser.parse_args()

    save_files = False
    if args.save_ids is not None or args.range_ids is not None:
        save_files = True

    if (args.plot_ids is None and not save_files) or not args.beamline:
        parser.print_help()
        parser.exit()

    return args, save_files


def parse_range_ids(range_str):
    range_list = range_str.split(':')
    assert len(range_list) == 2, \
        '{}: provided value is incorrect. The value must consist of two integers separated by colon.'.format(range_str)
    first_id = int(range_list[0])
    last_id = int(range_list[1])
    assert last_id >= first_id, 'Got first id ({}) > last id ({})'.format(first_id, last_id)
    return list(range(first_id, last_id + 1))


def parse_scan_ids(scans_list):
    try:
        scan_ids = [int(x) for x in scans_list]
    except:
        raise ValueError('Incorrect scan ids provided: {}'.format(scans_list))
    if not scan_ids:
        scan_ids = [-1]
    return scan_ids


def parse_studies():
    parser = argparse.ArgumentParser(description='Select a study to fit by parabola')
    parser.add_argument('-b', '--beamline', dest='beamline', default=None, choices=('chx', 'CHX', 'smi', 'SMI'),
                        help='select beamline to get data from')
    parser.add_argument('-s', '--study', dest='study', default=None, choices=('elevation', 'taper'),
                        help='study name')
    parser.add_argument('-n', '--no-save', dest='no_save', default=None, action='store_true',
                        help='do not save files')
    args = parser.parse_args()

    if args.study is None:
        parser.print_help()
        parser.exit()

    return args


def read_config(beamline, config_dir='config', config_file='beamlines.json'):
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        config_dir,
        config_file,
    )
    if not os.path.isfile(config_path):
        raise ValueError('{}: JSON config file not found'.format(config_path))
    with open(config_path) as f:
        config_dict = json.load(f)
    return config_dict[beamline.upper()]
