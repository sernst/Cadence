# TrackwayNormalityFigures.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import numpy as np
from scipy import stats as spStats

from plotly import plotly
from plotly import graph_objs as plotlyGraph

from pyaid.color.ColorValue import ColorValue

from cadence.analysis.shared import DataLoadUtils, PlotConfigs


#_______________________________________________________________________________
def makeTrackwayBox(site, data, columnName, **kwargs):

    traces = []
    for trackway in data.trackwayName.unique():
        dataSlice = data[data.trackwayName == trackway]
        if dataSlice.shape[0] > 19:
            test = spStats.normaltest(dataSlice[columnName].values)
            threshold = 3.5
            color = ColorValue({
                'r':max(0, min(255, 255.0*(test[0]/threshold))),
                'g':max(0, min(255, 255.0 - 255.0*(test[0]/threshold))),
                'b':0.0})
        else:
            test = (100, 1.0)
            color = ColorValue('#999999')

        name = trackway.split('-')[1:]
        name = '%s (%s) %s-%s' % (name[0], name[2], name[3], name[4])

        traces.append(plotlyGraph.Box(
            name=name,
            y=dataSlice[columnName].values,
            boxmean=True,
            marker=plotlyGraph.Marker(
                size=1,
                color=color.webRGBA),
            boxpoints='all' ))

    if not traces:
        return

    data = plotlyGraph.Data(traces)
    layout = plotlyGraph.Layout(
        showlegend=False,
        title='%s Trackway "%s" Distributions' % (site, columnName))

    url = plotly.plot(
        filename='A16/%s-%s-distributions' % (site, columnName),
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print('TRACKWAY_BOX[%s]:' % site, url)

################################################################################
################################################################################

#_______________________________________________________________________________ _main_
def _main_(args):
    tracks = DataLoadUtils.getTrackWithAnalysis()
    tracks = tracks[(tracks.width > 0) & (tracks.length > 0)]

    for site in tracks.site.unique():
        dataSlice = tracks[(tracks.site == site) & tracks.pes]
        makeTrackwayBox(
            site=site,
            data=dataSlice,
            columnName='width')

#_______________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        Plots basic figures for SVP talk.""")
    _main_(parser.parse_args())



