import datetime
import time


def current_timestamp():
    return time.time()


def current_time(offset_hours=0, for_file_name=False):
    kwargs = {}
    if for_file_name:
        kwargs['time_format'] = '%Y-%m-%d_%H-%M-%S'
    return humanize_time(current_timestamp() + offset_hours * 3600, **kwargs)


def humanize_time(timestamp, time_format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.fromtimestamp(timestamp=timestamp).strftime(time_format)
