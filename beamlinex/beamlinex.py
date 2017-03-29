#!/usr/bin/python
# -*- coding: utf-8 -*-

import beamlinex.common.command_line as cl
import beamlinex.common.io as c_io
import beamlinex.common.plot as c_plot


def beamlinex_cli():
    args, save_files = cl.parse_command_line()

    config_dict = cl.read_config(beamline=args.beamline)
    x_label = args.x_label if args.x_label else cl.get_beamline_labels(config_dict=config_dict, label='x_label')
    y_label = args.y_label if args.y_label else cl.get_beamline_labels(config_dict=config_dict, label='y_label')
    x_units = args.x_units if args.x_units else cl.get_beamline_units(config_dict=config_dict, units='x_units')
    y_units = args.y_units if args.y_units else cl.get_beamline_units(config_dict=config_dict, units='y_units')

    plot_kwargs = {
        'timestamp': args.timestamp,
        'extension': args.graph_extension,
        'norm': args.norm_plots,
        'x_label': x_label,
        'y_label': y_label,
        'x_units': x_units,
        'y_units': y_units,
        'convert_to_energy': args.convert_to_energy,
    }
    if args.scatter_size:
        plot_kwargs['scatter_size'] = args.scatter_size

    save_kwargs = {
        'timestamp': args.timestamp,
        'extension': args.data_extension,
        'columns': args.columns,
        'index': args.hide_index_column,
    }

    if args.plot_ids is not None:
        c_plot.plot_scans(scan_ids=cl.parse_scan_ids(args.plot_ids), **plot_kwargs)

    if save_files:
        if args.save_ids is not None:
            scan_ids = cl.parse_scan_ids(args.save_ids)
        else:
            scan_ids = cl.parse_range_ids(args.range_ids)

        print('The following scan ids will be saved: {} ({} scans)'.format(scan_ids, len(scan_ids)))
        for scan_id in scan_ids:
            c_plot.plot_scans(scan_ids=[scan_id], show=False, **plot_kwargs)
            file_name = c_io.save_data(scan_id=scan_id, **save_kwargs)
            print('    Saved {}'.format(file_name))


if __name__ == '__main__':
    beamlinex_cli()
