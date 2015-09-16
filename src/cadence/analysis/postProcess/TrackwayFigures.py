# TrackwayFigures.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import numpy as np
import pandas as pd

from refined_stats.density import DensityDistribution

from plotly import plotly
from plotly import graph_objs as plotlyGraph
from pyaid.color.ColorValue import ColorValue
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.shared import DataLoadUtils, PlotConfigs
from cadence.analysis.stats.StatisticsAnalyzer import StatisticsAnalyzer
from cadence.analysis.stats.TrackwayStatsStage import TrackwayStatsStage

#_______________________________________________________________________________
def getScatterPlotBounds(data, columnName, errorColumnName =None):
    column = data[columnName]
    bounds = (column.min(), column.max())
    delta = abs(bounds[1] - bounds[0])

    bounds = (
        bounds[0] - 0.1*delta,
        bounds[1] + 0.1*delta)

    if not errorColumnName:
        return bounds

    errorColumn = data[errorColumnName]
    return (
        min(bounds[0], (column - errorColumn).min()),
        max(bounds[1], (column + errorColumn).max()) )

#_______________________________________________________________________________
def makeTrackwayScatter(data, xName, yName, **kwargs):

    xBounds = getScatterPlotBounds(data, xName, kwargs.get('xErrName'))
    yBounds = getScatterPlotBounds(data, yName, kwargs.get('yErrName'))

    traces = []
    for sitemapName in data['Sitemap Name'].unique():
        color = PlotConfigs.SITE_SPECS[sitemapName]['color']
        dataSlice = data[data['Sitemap Name'] == sitemapName]
        plotKwargs = dict(
            x=dataSlice[xName].values,
            y=dataSlice[yName].values)
        if 'xErrName' in kwargs:
            plotKwargs['error_x'] = plotlyGraph.ErrorX(
                type='data',
                color=color,
                array=dataSlice[kwargs['xErrName']].values,
                visible=True)
        if 'yErrName' in kwargs:
            plotKwargs['error_y'] = plotlyGraph.ErrorY(
                type='data',
                color=color,
                array=dataSlice[kwargs['yErrName']].values,
                visible=True)

        traces.append(plotlyGraph.Scatter(
            name=sitemapName,
            mode='markers',
            marker=plotlyGraph.Marker(color=color),
            **plotKwargs))

    data = plotlyGraph.Data(traces)
    layout = plotlyGraph.Layout(
        title=kwargs.get('title', 'Trackway Plot'),
        xaxis=plotlyGraph.XAxis(
            title=kwargs.get('xLabel', xName),
            range=xBounds,
            autorange=False),
        yaxis=plotlyGraph.YAxis(
            title=kwargs.get('yLabel', yName),
            range=yBounds,
            autorange=False))

    plotName = 'A16/' + kwargs.get('name', 'trackway-%s-%s' % (
        xName.replace(' ', ''),
        yName.replace(' ', '') ))

    url = plotly.plot(
        filename=plotName,
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print('SCATTER["%s" vs "%s"]:' % (xName, yName), url)

#_______________________________________________________________________________
def makeStackedBars(
        label, dataFrame, columnName, errorColumnName,
        densityTraceFunction =None
):
    dataFrame = dataFrame[
        (dataFrame[columnName] > 0.0) &
        (dataFrame[errorColumnName] > 0.0 )]

    traces = []
    xStart = dataFrame[columnName].min()
    xEnd = dataFrame[columnName].max()
    binDelta = 0.01
    bins = [xStart]

    print(
        label,
        '\n * MEAN:', np.mean(dataFrame[columnName].values),
        '\n * MEDIAN:', np.median(dataFrame[columnName].values))

    while bins[-1] < xEnd:
        bins.append(min(xEnd, bins[-1] + binDelta))

    for site in dataFrame['Sitemap Name'].unique():
        color = PlotConfigs.SITE_SPECS[site]['color']
        siteSlice = dataFrame[dataFrame['Sitemap Name'] == site]
        data = np.histogram(a=siteSlice[columnName].values, bins=bins)
        traces.append(plotlyGraph.Bar(
            name=site,
            x=data[1],
            y=data[0],
            marker=plotlyGraph.Marker(color=color) ))

    if densityTraceFunction is not None:
        t, dd = densityTraceFunction(
            data=dataFrame,
            columnName=columnName,
            errorColumnName=errorColumnName,
            yaxis='y2',
            name='Density')
        print('DENSITY MEDIAN:', dd.getMedian())
        traces.append(t)
        suffix = ' With Density'
        yAxis2 = plotlyGraph.YAxis(
            title='Density',
            range=[0, round(max(t['y']))],
            overlaying='y',
            autorange=False,
            showline=False,
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            side='right')
    else:
        suffix = ''
        yAxis2 = None

    data = plotlyGraph.Data(traces)
    layout = plotlyGraph.Layout(
        title='%s Distributions by Tracksite%s' % (label, suffix),
        barmode='stack',
        xaxis=plotlyGraph.XAxis(
            title='Mean Track Width (m)',
            range=[xStart - 0.01, xEnd + 0.01],
            autorange=False ),
        yaxis=plotlyGraph.YAxis(
            title='Count',
            autorange=True))

    if suffix:
        layout.update(yaxis2=yAxis2)

    url = plotly.plot(
        filename='A16/%s-Trackway-Stacked-Distributions%s' % (
            label.replace(' ', '-'),
            '-With-Density' if suffix else ''),
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print('STACK[%s]:' % label, url)

#_______________________________________________________________________________
def makeComparison(data, unweightedData, columnName, label):
    unweightedColumnName = 'unweighted'
    wd  = data[[columnName, 'Name', 'Length']]
    wd  = wd[data[columnName] != 0.0].copy()

    uwd = unweightedData[[columnName, 'Name']]
    uwd = uwd[uwd[columnName] != 0.0].copy()
    uwd.rename(columns={columnName:unweightedColumnName}, inplace=True)

    d = pd.merge(
        left=wd,
        right=uwd,
        on='Name')

    d['Comparison'] = (d[unweightedColumnName] - d[columnName]).abs()
    d['Fractional'] = 100.0*d['Comparison']/d[columnName]

    d.sort(columns='Length', ascending=True, inplace=True)

    colors = []
    countMax = d['Length'].max()
    for count in d['Length'].values:
        if count < 11:
            c = ColorValue({
                'h':0.0,
                's':70.0 - 70.0*min(1.0, float(count - 1.0)/10.0),
                'v':100.0 - 50.0*min(1.0, float(count - 1.0)/10.0) })
        else:
            c = ColorValue({
                'h':240.0,
                's':70.0*min(1.0, float(count - 10)/20.0),
                'v':50.0 + 50.0*min(1.0, float(count - 10)/20.0) })
        colors.append(c.webRGBA)

    data = plotlyGraph.Data([
        plotlyGraph.Bar(
            x=d['Name'],
            y=d['Fractional'],
            text=d['Length'].map(lambda x: 'Count: %s' % x),
            marker=plotlyGraph.Marker(
                color=colors) ) ])

    layout = plotlyGraph.Layout(
        title='%s Uncertainty-Weighting Comparison (Per-Trackway)' % label,
        yaxis=plotlyGraph.YAxis(
            title='Difference (%)'),
        xaxis=plotlyGraph.XAxis(
            title='Trackway',
            showticklabels=False) )

    url = plotly.plot(
        filename='A16/%s-Weighted-Comparison' % label.replace(' ', '-'),
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print('COMPARISON[%s]:' % label, url)

#_______________________________________________________________________________
def getDensityDistributionTrace(data, columnName, errorColumnName, **kwargs):
    minVal = (data[columnName] - 3.0*data[errorColumnName]).min()
    maxVal = (data[columnName] + 3.0*data[errorColumnName]).max()

    values = []
    for index, row in data.iterrows():
        values.append(NumericUtils.toValueUncertainty(
            value=row[columnName],
            uncertainty=row[errorColumnName] ))

    dd = DensityDistribution(values=values)
    xValues = np.linspace(minVal, maxVal, 200)
    yValues = dd.createDistribution(xValues)

    return plotlyGraph.Scatter(
        x=xValues,
        y=yValues,
        **kwargs), dd

#_______________________________________________________________________________
def makeDensityDistribution(label, dataFrame, columnName, errorColumnName):
    dataFrame = dataFrame[
        (dataFrame[columnName] > 0.0) &
        (dataFrame[errorColumnName] > 0) ]

    trace, dd = getDensityDistributionTrace(
        data=dataFrame,
        columnName=columnName,
        errorColumnName=errorColumnName,
        fill='tozeroy')
    data = plotlyGraph.Data([trace])

    layout = plotlyGraph.Layout(
        title='%s Density Distribution' % label,
        yaxis=plotlyGraph.YAxis(
            title='Density'),
        xaxis=plotlyGraph.XAxis(
            title=label) )

    url = plotly.plot(
        filename='A16/%s-Density-Distribution' % label.replace(' ', '-'),
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print('DENSITY[%s]:' % label, url)

#_______________________________________________________________________________
def makeDensityDistributionComparison(
        label, dataFrame, unweightedDataFrame, columnName, errorColumnName
):
    dataFrame = dataFrame[
        (dataFrame[columnName] > 0.0) &
        (dataFrame[errorColumnName] > 0) ]
    unweightedDataFrame = unweightedDataFrame[
        (unweightedDataFrame[columnName] > 0.0) &
        (unweightedDataFrame[errorColumnName] > 0) ]

    traces = [
        getDensityDistributionTrace(
            dataFrame, columnName, errorColumnName)[0],
        getDensityDistributionTrace(
            unweightedDataFrame, columnName, errorColumnName)[0] ]

    data = plotlyGraph.Data(traces)

    layout = plotlyGraph.Layout(
        title='%s Density Distribution Comparison' % label,
        yaxis=plotlyGraph.YAxis(
            title='Density'),
        xaxis=plotlyGraph.XAxis(
            title=label) )

    url = plotly.plot(
        filename='A16/%s-Density-Distribution-Comparison' %
                 label.replace(' ', '-'),
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print('DENSITY-COMPARISON[%s]:' % label, url)

################################################################################
################################################################################

#_______________________________________________________________________________ _main_
def _main_(args):
    dFrame = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename=TrackwayStatsStage.TRACKWAY_STATS_CSV)

    unweightedDFrame = DataLoadUtils.getAnalysisData(
        analyzerClass=StatisticsAnalyzer,
        filename=TrackwayStatsStage.UNWEIGHTED_TRACKWAY_STATS_CSV)

    for d in [dFrame, unweightedDFrame]:
        d['Sitemap Name'] = d['Name'].str[:3]
        d['Fractional Pes Width Uncertainty'] = \
            100.0*d['Pes Width Uncertainty']/d['Pes Width']

    items = [
        dict(
            label='Pes Width',
            colName='Pes Width',
            errColName='Pes Width Uncertainty'),
        dict(
            label='Manus Width',
            colName='Manus Width',
            errColName='Manus Width Uncertainty') ]

    for item in items:
        makeStackedBars(
            label='Unweighted %s' % item['label'],
            dataFrame=unweightedDFrame,
            columnName=item['colName'],
            errorColumnName=item['errColName'])

        makeStackedBars(
            label='Unweighted %s' % item['label'],
            dataFrame=unweightedDFrame,
            columnName=item['colName'],
            errorColumnName=item['errColName'],
            densityTraceFunction=getDensityDistributionTrace)

        makeStackedBars(
            label=item['label'],
            dataFrame=dFrame,
            columnName=item['colName'],
            errorColumnName=item['errColName'])

        makeStackedBars(
            label=item['label'],
            dataFrame=dFrame,
            columnName=item['colName'],
            errorColumnName=item['errColName'],
            densityTraceFunction=getDensityDistributionTrace)

        makeDensityDistribution(
            label=item['label'],
            dataFrame=dFrame,
            columnName=item['colName'],
            errorColumnName=item['errColName'])

        makeDensityDistributionComparison(
            label=item['label'],
            dataFrame=dFrame,
            unweightedDataFrame=unweightedDFrame,
            columnName=item['colName'],
            errorColumnName=item['errColName'])

        makeComparison(
            data=dFrame,
            unweightedData=unweightedDFrame,
            columnName=item['colName'],
            label=item['label'])

    makeComparison(dFrame, unweightedDFrame, 'Pes Length', 'Pes Length')
    makeComparison(dFrame, unweightedDFrame, 'Stride Length', 'Stride Length')
    makeComparison(dFrame, unweightedDFrame, 'Pace Length', 'Pace Length')

    for entry in [('', dFrame), ('Unweighted', unweightedDFrame)]:
        label = entry[0]
        d = entry[1]
        titlePrefix = ('%s ' % label) if label else ''
        prefix = ('%s-' % label.lower()) if label else ''

        makeTrackwayScatter(
            name='%strackway-count-width-unc' % prefix,
            data=d[(d['Pes Width'] > 0) & (d['Pes Length'] > 0)],
            xName='Length',
            yName='Fractional Pes Width Uncertainty',
            title='%sStandard Error Track Width vs Track Count' % titlePrefix,
            xLabel='Track Count (#)',
            yLabel='Track Width Uncertainty (%)')

        makeTrackwayScatter(
            name='%strackway-pes-length-width' % prefix,
            data=d[(d['Pes Width'] > 0) & (d['Pes Length'] > 0)],
            xName='Pes Width',
            yName='Pes Length',
            xErrName='Pes Width Uncertainty',
            yErrName='Pes Length Uncertainty',
            title='%sTrackway Pes Length vs Width' % titlePrefix,
            xLabel='Width (m)',
            yLabel='Length (m)')

        makeTrackwayScatter(
            name='%strackway-manus-length-width' % prefix,
            data=d[(d['Manus Width'] > 0) & (d['Manus Length'] > 0)],
            xName='Manus Width',
            yName='Manus Length',
            xErrName='Manus Width Uncertainty',
            yErrName='Manus Length Uncertainty',
            title='%sTrackway Manus Length vs Width' % titlePrefix,
            xLabel='Width (m)',
            yLabel='Length (m)')

#_______________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        Plots trackway statistics figures for SVP talk.""")
    _main_(parser.parse_args())



