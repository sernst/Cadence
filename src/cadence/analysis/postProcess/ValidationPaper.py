# ValidationPaper.py
# (C)2015
# Scott Ernst

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import locale

import numpy as np
import pandas as pd
from scipy.stats import norm
from plotly import plotly
import plotly.graph_objs as plotlyGraph

from cadence.analysis.comparison.ComparisonAnalyzer import ComparisonAnalyzer
from cadence.analysis.shared import DataLoadUtils, PlotConfigs
from cadence.analysis.shared.plotting import PlotlyUtils
from cadence.analysis.validation.ValidationAnalyzer import ValidationAnalyzer

################################################################################

locale.setlocale(locale.LC_ALL, ('en_US', 'utf8'))

PLOTLY_FOLDER = 'Comparison'

#_______________________________________________________________________________
def plotComparison(df, key, label, binCount):

    xMin = df[key].min()
    xMax = df[key].max()

    count = df.shape[0]
    test = np.histogram(
        a=df[key].values,
        bins=np.linspace(xMin, xMax, 512))
    cdf = 100.0*np.cumsum(test[0])/float(count)
    for i in range(len(cdf)):
        if cdf[i] >= 98.0:
            xMax = test[1][i]
            break

    areaTraces = []
    xValues = np.linspace(xMin, xMax, 64)
    areaValues = np.zeros(len(xValues) - 1)

    histTraces = []
    bins = np.linspace(xMin, xMax, int(binCount))

    index = 0
    for sizeClass in PlotConfigs.SIZE_CLASSES:
        color = sizeClass['color']
        dataSlice = df[
            (df['width'] >= sizeClass['range'][0]) &
            (df['width'] < sizeClass['range'][1] )]
        sliceCountLabel = locale.format(
            '%d', int(dataSlice.shape[0]), grouping=True)
        histValues = np.histogram(a=dataSlice[key].values, bins=bins)
        histTraces.append(plotlyGraph.Bar(
            name='%s (%s)' % (sizeClass['name'], sliceCountLabel),
            x=100.0*histValues[1],
            y=histValues[0],
            marker=plotlyGraph.Marker(color=color) ))

        histValues = np.histogram(a=dataSlice[key].values, bins=xValues)
        values = 100.0*(dataSlice.shape[0] - np.cumsum(histValues[0]))/count
        areaValues = np.add(areaValues, values)
        areaTraces.append(plotlyGraph.Scatter(
            name='%s (%s)' % (sizeClass['name'], sliceCountLabel),
            x=100.0*histValues[1],
            y=areaValues,
            mode='lines',
            fill='tozeroy' if index < 1 else 'tonexty',
            line=plotlyGraph.Line(
                width=1.0,
                color=color) ))

        index += 1

    countLabel = locale.format('%d', count, grouping=True)

    data = plotlyGraph.Data(histTraces)
    layout = plotlyGraph.Layout(
        title='Distribution of Track %s Deviations (%s Tracks)' % (
            label, countLabel),
        barmode='stack',
        xaxis=plotlyGraph.XAxis(
            title='Deviation (%)'),
        yaxis=plotlyGraph.YAxis(
            title='Frequency',
            autorange=True))

    url = plotly.plot(
        filename=PlotlyUtils.getPlotlyFilename(
            filename='%s' % label.replace(' ', '-'),
            folder=PLOTLY_FOLDER),
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print(
        'COMPARE|HIST[%s]' % label,
        'x:(%s, %s)' % (xMin, xMax),
        PlotlyUtils.toEmbedUrl(url))

    expected = []
    for x in xValues:
        expected.append(100.0*(1.0 - (norm.cdf(x) - norm.cdf(-x))))

    areaTraces.append(plotlyGraph.Scatter(
        name='Normal Threshold',
        x=100.0*xValues,
        y=expected,
        mode='lines',
        line=plotlyGraph.Line(
            color='rgba(0, 0, 0, 0.75)',
            dash='dash',
            width=1.0) ))

    data = plotlyGraph.Data(areaTraces)
    layout = plotlyGraph.Layout(
        title=('Inverse Cumulative Distribution of Track ' +
            '%s Deviations (%s Tracks)') % (label, countLabel),
        xaxis=plotlyGraph.XAxis(
            title='Deviation (%)',
            range=[100.0*xMin, 100.0*xMax],
            autorange=False),
        yaxis=plotlyGraph.YAxis(
            title='Cumulative Remainder (%)',
            range=[0, 100],
            autorange=False))

    url = plotly.plot(
        filename=PlotlyUtils.getPlotlyFilename(
            filename='%s-cdf-remainder' % label.replace(' ', '-'),
            folder=PLOTLY_FOLDER),
        figure_or_data=plotlyGraph.Figure(data=data, layout=layout),
        auto_open=False)
    print(
        'COMPARE|AREA[%s]' % label,
        'x:(%s, %s)' % (xMin, xMax),
        PlotlyUtils.toEmbedUrl(url))

################################################################################

#_______________________________________________________________________________
def _main_(args):

    #---------------------------------------------------------------------------
    # TRACK LENGTH & WIDTH
    df = DataLoadUtils.getAnalysisData(
        analyzerClass=ComparisonAnalyzer,
        filename='Length-Width-Deviations.csv')
    df['site'] = df['Fingerprint'].str[:3]

    tracks = DataLoadUtils.getTrackWithAnalysis()
    df = pd.merge(
        df, tracks[['uid', 'width']],
        left_on='UID',
        right_on='uid')

    plotComparison(
        label='Width',
        key='Width Deviation',
        df=df[df['Width Deviation'] >= 0.0],
        binCount=10.0)

    plotComparison(
        label='Length',
        key='Length Deviation',
        df=df[df['Length Deviation'] >= 0.0],
        binCount=10.0)

    #---------------------------------------------------------------------------
    # STRIDE LENGTH
    df = DataLoadUtils.getAnalysisData(
        analyzerClass=ValidationAnalyzer,
        filename='Stride-Length-Deviations.csv')
    df['site'] = df['Fingerprint'].str[:3]
    df = pd.merge(
        df, tracks[['uid', 'width']],
        left_on='UID',
        right_on='uid')

    plotComparison(
        label='Stride Length',
        key='Deviation',
        df=df,
        binCount=10.0)

    #---------------------------------------------------------------------------
    # PACE LENGTH
    df = DataLoadUtils.getAnalysisData(
        analyzerClass=ValidationAnalyzer,
        filename='Pace-Length-Deviations.csv')
    df['site'] = df['Fingerprint'].str[:3]
    df = pd.merge(
        df, tracks[['uid', 'width']],
        left_on='UID',
        right_on='uid')

    plotComparison(
        label='Pace Length',
        key='Deviation',
        df=df,
        binCount=10.0)

#_______________________________________________________________________________
if __name__ == '__main__':
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        ValidationPaper does...""")

    _main_(parser.parse_args())
