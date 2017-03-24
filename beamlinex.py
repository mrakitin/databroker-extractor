#!/usr/bin/python
# -*- coding: utf-8 -*-

import common.command_line as cl
import common.io as c_io
import common.plot as c_plot

if __name__ == '__main__':
    import argparse

    # Plot a single graph:
    parser = argparse.ArgumentParser(description='Visualize data for NSLS-II beamlines')
    # Plot data:
    parser.add_argument('-p', '--plot-ids', dest='plot_ids', default=None, nargs='*',
                        help='plot data for blank-separated scan ids list')
    parser.add_argument('-n', '--norm-plots', dest='norm_plots', default=None, choices=('total', 'individual'),
                        help='normalize plots')
    parser.add_argument('-x', '--x-label', dest='x_label', default=None, help='x label to plot')
    parser.add_argument('-y', '--y-label', dest='y_label', default=None, help='y label to plot')

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

    if args.plot_ids is None and not save_files:
        parser.print_help()
        parser.exit()

    if args.plot_ids is not None:
        scan_ids = cl.parse_scan_ids(args.plot_ids)
        kwargs = {
            'scan_ids': scan_ids,
            'norm': args.norm_plots,
            'timestamp': args.timestamp,
            'extension': args.graph_extension,
        }
        if args.x_label:
            kwargs['x_label'] = args.x_label
        if args.y_label:
            kwargs['y_label'] = args.y_label

        c_plot.plot_scans(**kwargs)

    if save_files:
        if args.save_ids is not None:
            scan_ids = cl.parse_scan_ids(args.save_ids)
        else:
            scan_ids = cl.parse_range_ids(args.range_ids)

        print('The following scan ids will be saved: {}'.format(scan_ids))
        for scan_id in scan_ids:
            kwargs = {
                'timestamp': args.timestamp,
                'extension': args.graph_extension,
            }
            c_plot.plot_scans(
                scan_ids=[scan_id],
                x_label=args.x_label,
                y_label=args.y_label,
                norm=args.norm_plots,
                show=False,
                **kwargs
            )

            kwargs['extension'] = args.data_extension
            file_name = c_io.save_data(
                scan_id=scan_id,
                columns=args.columns,
                index=args.hide_index_column,
                **kwargs
            )
            print('    Saved {}'.format(file_name))
