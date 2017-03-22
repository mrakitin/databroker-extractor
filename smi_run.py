import common.command_line as cl
from smi.smidb import plot_scans, save_data

if __name__ == '__main__':
    import argparse

    # Plot a single graph:
    parser = argparse.ArgumentParser(description='Visualize data for NSLS-II SMI beamline')
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
    parser.add_argument('-c', '--columns-from-plots', dest='columns_from_plots', action='store_true',
                        help='save columns from plots')
    parser.add_argument('-i', '--hide-index-column', dest='hide_index_column', action='store_false',
                        help='hide index column in the saved file(s)')

    args = parser.parse_args()

    if args.plot_ids is None and args.save_ids is None:
        parser.print_help()
        parser.exit()

    if args.plot_ids is not None:
        scan_ids = cl.parse_scan_ids(args.plot_ids)
        kwargs = {
            'scan_ids': scan_ids,
            'norm': args.norm_plots,
        }
        if args.x_label:
            kwargs['x_label'] = args.x_label
        if args.y_label:
            kwargs['y_label'] = args.y_label
        plot_scans(**kwargs)

    if args.save_ids is not None:
        scan_ids = cl.parse_scan_ids(args.save_ids)
        for scan_id in scan_ids:
            plot_scans(scan_ids=[scan_id], show=False)
            file_name = save_data(
                scan_id=scan_id,
                columns_from_plots=args.columns_from_plots,
                index=args.hide_index_column,
            )
            print('Saved {}'.format(file_name))
