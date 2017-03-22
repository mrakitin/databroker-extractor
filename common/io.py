import numpy as np


def save_data_pandas(file_name, data, columns, index, justify='left'):
    with open(file_name, 'w') as f:
        f.write(data.to_string(columns=columns, index=index, justify=justify))


def save_data_numpy(data, name, header=None):
    kwargs = {}
    if header:
        kwargs['header'] = header
    np.savetxt(
        name,
        data,
        **kwargs
    )
