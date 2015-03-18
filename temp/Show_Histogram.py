from __future__ import print_function, absolute_import, unicode_literals, division

import matplotlib.pyplot as plt

def histogram(path, data, bins, xLimits, yLimits, color, isLog, title, xLabel, yLabel, **kwargs):
    plt.hist(data, bins, range=xLimits, facecolor=color, log=isLog)
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.xlim(*xLimits)
    plt.ylim(*yLimits)
    plt.grid(True)

    figure.savefig(path, **kwargs)
