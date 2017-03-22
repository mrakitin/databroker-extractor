from PIL import Image
from matplotlib import pyplot as plt


def save_raw_image(data, name):
    im = Image.fromarray(data).convert('L')
    im.save(name)


def clear_plt():
    """Clear the plots (useful when plotting in a loop).

    :return: None
    """
    plt.cla()
    plt.clf()
    plt.close()
