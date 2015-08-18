# BasicFigures.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import math

from plotly import plotly
from plotly import graph_objs as plotlyGraph
from plotly import tools as plotlyTools
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.shared import DataLoadUtils

SITE_SPECS = dict(
    CRO=dict(
        color='rgb(141,211,199)'),
    CRT=dict(
        color='rgb(188,128,189)'),
    BEB=dict(
        color='rgb(190,186,218)'),
    BSY=dict(
        color='rgb(251,128,114)'),
    PMM=dict(
        color='rgb(128,177,211)'),
    SCR=dict(
        color='rgb(253,180,98)'),
    TCH=dict(
        color='rgb(179,222,105)'),
    CPP=dict(
        color='rgb(252,205,229)'),
    OFF=dict(
        color='rgb(217,217,217)'))

def makePlot(label, tracks):
    tracks = tracks.copy()

    xBounds = [
        NumericUtils.roundToOrder(tracks.length.min() - 0.05, -1, math.floor),
        NumericUtils.roundToOrder(tracks.length.max() + 0.05, -1, math.ceil)]
    yBounds = [
        NumericUtils.roundToOrder(tracks.width.min() - 0.05, -1, math.floor),
        NumericUtils.roundToOrder(tracks.width.max() + 0.05, -1, math.ceil)]

    fig = plotlyTools.make_subplots(
        rows=1, cols=2,
        subplot_titles=('Length vs Width','Aspect Ratios'))

    traces = []
    for site in tracks.site.unique():
        color = SITE_SPECS[site]['color']
        siteSlice = tracks[tracks.site == site]
        traces.append(plotlyGraph.Scatter(
            name=site,
            mode='markers',
            xaxis='x1', yaxis='y1',
            marker=plotlyGraph.Marker(color=color),
            x=siteSlice.length,
            y=siteSlice.width))

        traces.append(plotlyGraph.Box(
            name=site,
            y=siteSlice.length/siteSlice.width,
            marker=plotlyGraph.Marker(color=color),
            xaxis='x2', yaxis='y2'))

    fig['data'] += plotlyGraph.Data(traces)
    fig['layout'].update(
        title='%s Length & Width by Tracksite' % label,
        xaxis1=plotlyGraph.XAxis(
            title='Length (m)',
            range=xBounds,
            autorange=False ),
        yaxis1=plotlyGraph.YAxis(
            title='Width (m)',
            range=yBounds,
            autorange=False ))

    url = plotly.plot(
        filename='A16/%s-Length-Width' % label,
        figure_or_data=fig)
    print('PLOT:', url)

tracks = DataLoadUtils.readTable('tracks')
tracks = tracks[(tracks.length > 0) & (tracks.width > 0)]

makePlot('Pes', tracks[tracks.pes])
makePlot('Manus', tracks[~tracks.pes])


