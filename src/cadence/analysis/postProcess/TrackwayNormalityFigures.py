# TrackwayNormalityFigures.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import re

import numpy as np

from pyaid.number.NumericUtils import NumericUtils
from plotly import plotly
from plotly import graph_objs as plotlyGraph
from plotly import tools as plotlyTools
from pyaid.color.ColorValue import ColorValue
from pyaid.string.StringUtils import StringUtils

from refined_stats.density import DensityDistribution
from cadence.analysis.shared import DataLoadUtils, PlotConfigs
from cadence.analysis.stats.StatisticsAnalyzer import StatisticsAnalyzer

NORMAL_THRESHOLD = 0.5

#_______________________________________________________________________________
def getNormalityColor(normality, goodChannel, badChannel):
    if NumericUtils.equivalent(normality, -1.0, 0.01):
        return ColorValue({'r':100, 'g':100, 'b':100})

    test  = min(1.0, max(0.0, normality))
    limit = NORMAL_THRESHOLD
    slope = 1.0/(1.0 - limit)
    intercept = -slope*limit
    test = min(1.0, max(0.0, slope*test + intercept))

    color = dict(r=0.0, b=0.0, g=0.0)
    color[badChannel] = max(0, 255.0*min(1.0, 1.0 - 1.0*test))
    color[goodChannel] = max(0, min(255, 255.0*test))
    return ColorValue(color)

#_______________________________________________________________________________
def makeNormalityScatter(label, trackwayData):
    fig = plotlyTools.make_subplots(
        rows=2, cols=2,
        print_grid=False,
        specs=[[{'rowspan':2}, {}], [None, {}]])

    key = 'Normality'
    unweightedKey = 'Unweighted Normality'

    df = trackwayData.copy()
    df['Sitemap Name'] = df['Name'].str[:3]
    df[key] = df[key].map(lambda x: min(1.0, max(0.0, x)))
    df[unweightedKey] = df[unweightedKey].map(lambda x: min(1.0, max(0.0, x)))

    xStart = min(df[key].min(), df[unweightedKey].min())
    xEnd = min(df[key].max(), df[unweightedKey].max())
    binDelta = 0.01
    bins = [xStart]

    while bins[-1] < xEnd:
        bins.append(min(xEnd, bins[-1] + binDelta))

    traces = []
    for site in df['Sitemap Name'].unique():
        dataSlice = df[df['Sitemap Name'] == site]
        color = PlotConfigs.SITE_SPECS[site]['color']

        traces.append(plotlyGraph.Scatter(
            name=site,
            x=dataSlice[unweightedKey].values,
            y=dataSlice[key].values,
            xaxis='x1',
            yaxis='y1',
            mode='markers',
            marker=plotlyGraph.Marker(color=color),
            text=dataSlice['Name']))


        data = np.histogram(a=dataSlice[unweightedKey].values, bins=bins)
        traces.append(plotlyGraph.Bar(
            name=site,
            x=data[1],
            y=data[0],
            xaxis='x2',
            yaxis='y2',
            marker=plotlyGraph.Marker(color=color) ))

        data = np.histogram(a=dataSlice[key].values, bins=bins)
        traces.append(plotlyGraph.Bar(
            name=site,
            x=data[1],
            y=data[0],
            xaxis='x3',
            yaxis='y3',
            marker=plotlyGraph.Marker(color=color) ))

    fig['data'] += plotlyGraph.Data(traces)
    fig['layout'].update(
        barmode='stack',
        yaxis1=plotlyGraph.YAxis(
            title='Weighted Normality (AU)',
            autorange=False,
            range=[0.0, 1.0]),
        yaxis2=plotlyGraph.YAxis(title='Unweighted'),
        yaxis3=plotlyGraph.YAxis(title='Weighted'),
        xaxis1=plotlyGraph.XAxis(
            title='Unweighted Normality (AU)',
            autorange=False,
            range=[0.0, 1.0]),
        xaxis2=plotlyGraph.XAxis(
            autorange=False,
            range=[0.0, 1.0]),
        xaxis3=plotlyGraph.XAxis(
            autorange=False,
            range=[0.0, 1.0]),
        title='%s Trackway Normality Comparison' % label)

    url = plotly.plot(
        filename='A16/%s-normality-comparison' % label.replace(' ', '-'),
        figure_or_data=fig,
        auto_open=False)
    print('COMPARISON[%s]:' % label, url)

#_______________________________________________________________________________
def makeTrackwayBoxTrace(trackwayRow, values, **kwargs):
    dd = DensityDistribution.fromValuesOnly(values=values)

    normality = trackwayRow['Unweighted Normality'].values \
        if trackwayRow is not None \
        else -1

    color = getNormalityColor(normality, 'b', 'r')
    color.opacity = 0.75

    values = dd.getDistributionPoints(2048)

    return plotlyGraph.Box(
        boxpoints=False,
        name=trackwayRow['Name'].values,
        y=values,
        boxmean=False,
        fillcolor=color.webRGBA,
        line=plotlyGraph.Line(
            color=color.webRGBA,
            width=1),
        marker=plotlyGraph.Marker(
            size=1,
            color=color.webRGBA) )

#_______________________________________________________________________________
def makeTrackwayWeightedBoxTrace(trackwayRow, values, uncertainties, **kwargs):
    dd = DensityDistribution.fromValuesAndUncertainties(
        values=values,
        uncertainties=uncertainties)
    values = dd.getDistributionPoints(2048)

    normality = trackwayRow['Normality'].values \
        if trackwayRow is not None \
        else -1

    color = getNormalityColor(normality, 'g', 'r')
    color.opacity = 0.5

    return plotlyGraph.Box(
        boxpoints=False,
        name=trackwayRow['Name'].values,
        y=values,
        fillcolor=color.webRGBA,
        boxmean=False,
        line=plotlyGraph.Line(
            color=color.webRGBA,
            width=1),
        marker=plotlyGraph.Marker(
            size=1,
            color=color.webRGBA) )

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

#_______________________________________________________________________________
def getColumnLabel(columnName):
    s1 = first_cap_re.sub(r'\1_\2', columnName)
    return all_cap_re.sub(r'\1_\2', s1).lower().replace('_', ' ')

#_______________________________________________________________________________
def makeTrackwayBox(
        site, data, columnName, errorColumnName, trackwayData, **kwargs
):

    label = getColumnLabel(columnName)
    traces = []
    for trackway in data.trackwayName.unique():
        dataSlice = data[data.trackwayName == trackway]
        values = dataSlice[columnName].values
        uncertainties = dataSlice[errorColumnName].values
        name = trackway.split('-')[1:]
        name = '%s:%s (%s) %s-%s' % (
            name[0],
            name[1][-2:],
            name[2],
            name[3],
            name[4])

        try:
            row = trackwayData[trackwayData['Name'] == trackway].iloc[[0]]
        except Exception:
            print('SKIPPED:', trackway, dataSlice.shape[0])
            continue

        traces.append(makeTrackwayWeightedBoxTrace(row, values, uncertainties))
        traces.append(makeTrackwayBoxTrace(row, values))

    if not traces:
        return

    title = StringUtils.capitalizeWords(columnName)

    data = plotlyGraph.Data(traces)
    layout = plotlyGraph.Layout(
        showlegend=False,
        yaxis=plotlyGraph.YAxis(
            title='%s Value' % label),
        xaxis=plotlyGraph.XAxis(
            title='Trackway',
            showticklabels=False ),
        title='%s Trackway "%s" Distributions' % (site, title))

    url = plotly.plot(
        filename='A16/%s-%s-distributions' % (site, label),
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print('TRACKWAY_BOX[%s]:' % site, url)

################################################################################
################################################################################

#_______________________________________________________________________________ _main_
def _main_(args):
    tracks = DataLoadUtils.getTrackWithAnalysis()
    tracks = tracks[(tracks.width > 0) & (tracks.length > 0)]

    df = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename='Stride-Length-Quartiles.csv')
    makeNormalityScatter('Stride Length', df)

    df = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename='Pace-Length-Quartiles.csv')
    makeNormalityScatter('Pace Length', df)

    for site in tracks.site.unique():
        dataSlice = tracks[(tracks.site == site) & tracks.pes]
        makeTrackwayBox(
            site=site,
            data=dataSlice,
            columnName='paceLength',
            errorColumnName='paceLengthUnc',
            trackwayData=df)

    df = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename='Manus-Width-Quartiles.csv')
    makeNormalityScatter('Manus Width', df)

    df = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename='Manus-Length-Quartiles.csv')
    makeNormalityScatter('Manus Length', df)

    df = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename='Pes-Length-Quartiles.csv')
    makeNormalityScatter('Pes Length', df)

    df = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename='Gauge-Quartiles.csv')
    makeNormalityScatter('Gauge', df)

    widthDFrame = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename='Pes-Width-Quartiles.csv')
    makeNormalityScatter('Pes Width', widthDFrame)

    for site in tracks.site.unique():
        dataSlice = tracks[(tracks.site == site) & tracks.pes]
        makeTrackwayBox(
            site=site,
            data=dataSlice,
            columnName='width',
            errorColumnName='widthUncertainty',
            trackwayData=widthDFrame)

#_______________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        Plots basic figures for SVP talk.""")
    _main_(parser.parse_args())



