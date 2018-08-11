from matplotlib import pyplot as plt
import matplotlib.dates as dt
import seaborn

seaborn.set()
import datetime


class Plot(object):
    def __init__(self):
        pass

    def make_bar(
        x,
        y,
        f_name,
        title=None,
        legend=None,
        x_label=None,
        y_label=None,
        x_ticks=None,
        y_ticks=None,
    ):
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

        plt.bar(x, y, align="center")

        if legend is not None:
            plt.legend(legend)

        plt.savefig(f_name)
        plt.close(fig)

    def make_line(
        x,
        y,
        f_name,
        title=None,
        legend=None,
        x_label=None,
        y_label=None,
        x_ticks=None,
        y_ticks=None,
    ):
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

        if isinstance(y[0], list):
            for data in y:
                plt.plot(x, data)
        else:
            plt.plot(x, y)

        if legend is not None:
            plt.legend(legend)

        plt.savefig(f_name)
        plt.close(fig)

    def make_efficiency_date(
        total_data,
        avg_data,
        f_name,
        title=None,
        x_label=None,
        y_label=None,
        x_ticks=None,
        y_ticks=None,
    ):

        fig = plt.figure()

        if title is not None:
            plt.title(title, fontsize=16)
        if x_label is not None:
            plt.ylabel(x_label)
        if y_label is not None:
            plt.xlabel(y_label)

        v_date = []
        v_val = []

        for data in total_data:
            dates = dt.date2num(datetime.datetime.strptime(data[0], "%H:%M"))
            to_int = round(float(data[1]))
            plt.plot_date(dates, data[1], color=plt.cm.brg(to_int))
        for data in avg_data:
            dates = dt.date2num(datetime.datetime.strptime(data[0], "%H:%M"))
            v_date.append(dates)
            v_val.append(data[1])

        plt.plot_date(v_date, v_val, "^y-", label="Average")
        plt.legend()
        plt.savefig(f_name)
        plt.close(fig)
