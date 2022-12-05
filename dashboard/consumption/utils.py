import matplotlib.dates as mdates

from consumption.constants import FONTNAME, Y_LABEL, SUMMARY_X_LABEL, DETAIL_X_LABEL


def plt_set_axis(ax1, ax2):
    ax1.set_xlabel(SUMMARY_X_LABEL, fontname=FONTNAME)
    ax1.set_ylabel(Y_LABEL, fontname=FONTNAME)
    formatter = mdates.DateFormatter("%m")
    ax1.xaxis.set_major_formatter(formatter)
    ax2.set_xlabel(DETAIL_X_LABEL, fontname=FONTNAME)
    ax2.set_ylabel(Y_LABEL, fontname=FONTNAME)
    formatter = mdates.DateFormatter("%d")
    ax2.xaxis.set_major_formatter(formatter)
