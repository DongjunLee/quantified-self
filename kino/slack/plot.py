import matplotlib
matplotlib.use('TkAgg')

from matplotlib import pyplot as plt
import seaborn; seaborn.set()

class Plot(object):

    def __init__(self):
        pass

    def make_bar(x, y, f_name, title=None,
                       x_label=None, y_label=None, x_ticks=None, y_ticks=None):
        fig = plt.figure()

        if title is not None:
            plt.title(title, fontsize=16)
        if x_label is not None:
            plt.ylabel(x_label)
        if y_label is not None:
            plt.xlabel(y_label)
        if x_ticks is not None:
            plt.xticks(x, x_ticks)
        if y_ticks is not None:
            plt.yticks(y_ticks)

        plt.bar(x, y, align='center')
        plt.savefig(f_name)
        plt.close(fig)

    def make_line(x, y, f_name, title=None,
                       x_label=None, y_label=None, x_ticks=None, y_ticks=None):
        fig = plt.figure()

        if title is not None:
            plt.title(title, fontsize=16)
        if x_label is not None:
            plt.ylabel(x_label)
        if y_label is not None:
            plt.xlabel(y_label)
        if x_ticks is not None:
            plt.xticks(x, x_ticks)
        if y_ticks is not None:
            plt.yticks(y_ticks)

        plt.plot(x, y)
        plt.savefig(f_name)
        plt.close(fig)
