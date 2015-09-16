# BasicFigures.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import math

import numpy as np
from plotly import plotly
from plotly import graph_objs as plotlyGraph
from plotly import tools as plotlyTools
from pyaid.number.NumericUtils import NumericUtils
from refined_stats.density import DensityDistribution

from cadence.analysis.shared import DataLoadUtils
from cadence.analysis.shared import PlotConfigs


#_______________________________________________________________________________
from cadence.analysis.shared.plotting import PlotlyUtils


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
        subplot_titles=('Length vs Width','Aspect Ratios'),
        print_grid=False)

    traces = []
    for site in tracks.site.unique():
        color = PlotConfigs.SITE_SPECS[site]['color']
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
        figure_or_data=fig,
        auto_open=False)
    print('PLOT[%s]:' % label, PlotlyUtils.toEmbedUrl(url))

#_______________________________________________________________________________
def makeHistograms(label, columnName, errorColumnName, tracks):
    index = 0
    histTraces = []
    densityTraces = []
    xStart = tracks[columnName].min()
    xEnd = tracks[columnName].max()
    sites = tracks.site.unique()
    for site in sites:
        index += 1
        color = PlotConfigs.SITE_SPECS[site]['color']
        siteSlice = tracks[tracks.site == site]
        histTraces.append(plotlyGraph.Histogram(
            name=site,
            x=siteSlice[columnName],
            autobinx=False,
            xbins=plotlyGraph.XBins(
                start=xStart,
                end=xEnd,
                size=0.01),
            xaxis='x1',
            yaxis='y%s' % int(index),
            marker=plotlyGraph.Marker(color=color) ))

        distributionValues = []
        for i, row in siteSlice.iterrows():
            distributionValues.append(NumericUtils.toValueUncertainty(
                value=row[columnName],
                uncertainty=row[errorColumnName]))

        dd = DensityDistribution(values=distributionValues)
        xValues = dd.getAdaptiveRange(10)
        yValues = dd.createDistribution(xValues=xValues, scaled=True)

        densityTraces.append(plotlyGraph.Scatter(
            name=site,
            x=xValues,
            y=yValues,
            xaxis='x1',
            yaxis='y%s' % int(index),
            mode='lines',
            fill='tozeroy',
            marker=plotlyGraph.Marker(color=color) ))

    fig = plotlyTools.make_subplots(
        rows=len(sites), cols=1,
        shared_xaxes=True,
        print_grid=False)
    fig['data'] += plotlyGraph.Data(histTraces)
    fig['layout'].update(title='%s Distributions by Tracksite' % label)

    url = plotly.plot(
        filename='A16/%s-Distributions' % label.replace(' ', '-'),
        figure_or_data=fig,
        auto_open=False)
    print('HISTOGRAM[%s]:' % label, PlotlyUtils.toEmbedUrl(url))

    fig = plotlyTools.make_subplots(
        rows=len(sites), cols=1,
        shared_xaxes=True,
        print_grid=False)
    fig['data'] += plotlyGraph.Data(densityTraces)
    fig['layout'].update(
        title='%s Distributions by Tracksite' % label,
        xaxis1=plotlyGraph.XAxis(
            autorange=False,
            range=[xStart, xEnd]))

    url = plotly.plot(
        filename='A16/%s-Kernel-Distributions' % label.replace(' ', '-'),
        figure_or_data=fig,
        auto_open=False)
    print('KERNEL-DENSITY[%s]:' % label, PlotlyUtils.toEmbedUrl(url))

#_______________________________________________________________________________
def makeStackedBars(label, columnName, tracks):
    traces = []
    xStart = tracks[columnName].min()
    xEnd = tracks[columnName].max()
    binDelta = 0.01
    bins = [xStart]

    while bins[-1] < xEnd:
        bins.append(min(xEnd, bins[-1] + binDelta))

    for site in tracks.site.unique():
        color = PlotConfigs.SITE_SPECS[site]['color']
        siteSlice = tracks[tracks.site == site]
        data = np.histogram(a=siteSlice[columnName].values, bins=bins)
        traces.append(plotlyGraph.Bar(
            name=site,
            x=data[1],
            y=data[0],
            marker=plotlyGraph.Marker(color=color) ))

    data = plotlyGraph.Data(traces)
    layout = plotlyGraph.Layout(
        title='%s Distributions by Tracksite' % label,
        barmode='stack',
        xaxis=plotlyGraph.XAxis(
            title='Track %s' % label,
            range=[xStart - 0.01, xEnd + 0.01],
            autorange=False ),
        yaxis=plotlyGraph.YAxis(
            title='Count',
            autorange=True))

    url = plotly.plot(
        filename='A16/%s-Stacked-Distributions' % label,
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print('STACK[%s]:' % label, PlotlyUtils.toEmbedUrl(url))

################################################################################
################################################################################

#_______________________________________________________________________________ _main_
def _main_(args):
    tracks = DataLoadUtils.getTrackWithAnalysis()
    tracks = tracks[(tracks.length > 0) & (tracks.width > 0)]

    pesTracks = tracks[tracks.pes]
    makePlot('Pes', pesTracks)

    df = pesTracks
    makeHistograms(
        label='Pes Width',
        columnName='width',
        errorColumnName='widthUncertainty',
        tracks=df)
    makeStackedBars('Pes Width', 'width', df)

    df = pesTracks[pesTracks['strideLength'] > 0]
    makeHistograms(
        label='Stride Length',
        columnName='strideLength',
        errorColumnName='strideLengthUnc',
        tracks=df)
    makeStackedBars('Stride Length', 'strideLength', df)

    df = pesTracks[pesTracks['paceLength'] > 0]
    makeHistograms(
        label='Pace Length',
        columnName='paceLength',
        errorColumnName='paceLengthUnc',
        tracks=df)
    makeStackedBars('Pace Length', 'paceLength', df)

    manusTracks = tracks[~tracks.pes]
    makePlot('Manus', manusTracks)

    makeHistograms(
        label='Manus Width',
        columnName='width',
        errorColumnName='widthUncertainty',
        tracks=manusTracks)
    makeStackedBars('Manus Width', 'width', manusTracks)

#_______________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        Plots basic figures for SVP talk.""")
    _main_(parser.parse_args())



