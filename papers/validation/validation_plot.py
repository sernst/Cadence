from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools
import json

from pyaid.file.FileUtils import FileUtils

import locale
import numpy as np
import pandas as pd
import plotly.graph_objs as plotlyGraph
from cadence.analysis.shared import DataLoadUtils, PlotConfigs
from cadence.analysis.shared.plotting import PlotlyUtils
from plotly import plotly

################################################################################

locale.setlocale(locale.LC_ALL, ('en_US', 'utf8'))

PLOTLY_FOLDER = 'Comparison'

MY_DIR = FileUtils.getDirectoryOf(__file__)
DATA_DIR = FileUtils.makeFolderPath(MY_DIR, 'data')
OUT_PATH = FileUtils.makeFilePath(DATA_DIR, 'deviation.h5')
METADATA_FILE = FileUtils.makeFilePath(DATA_DIR, 'deviation.metadata.json')

#_______________________________________________________________________________
def _getLayout(
        metadata, title, fixed = False, xAxis =None, yAxis =None, **kwargs
):
    if not xAxis:
        xAxis = {}
    xAxis.setdefault('title', 'Deviation (%)')

    if not yAxis:
        yAxis = {}
    yAxis.setdefault('title', 'Frequency')
    yAxis.setdefault('autorange', True)

    xAxis = plotlyGraph.XAxis(**xAxis)
    yAxis = plotlyGraph.YAxis(**yAxis)

    if fixed:
        xAxis['range'] = [
            100.0*metadata['xMin'],
            100.0*min(4.0, metadata['xMax']) ]
        xAxis['autorange'] = False

    return plotlyGraph.Layout(title=title, xaxis=xAxis, yaxis=yAxis, **kwargs)

#_______________________________________________________________________________
def _makeRemainder(key, sizeClass, areaValues, countLabel, isFirst):
    cdfDf = pd.read_hdf(OUT_PATH, key + 'cumulative')
    areaValues = np.add(areaValues, 100.0*cdfDf['y'][:-1])
    scatter = plotlyGraph.Scatter(
        name='%s (%s)' % (sizeClass['name'], countLabel),
        x=100.0*cdfDf['x'][:-1],
        y=areaValues,
        mode='lines',
        fill='tozeroy' if isFirst else 'tonexty',
        line=plotlyGraph.Line(
            width=1.0,
            color=sizeClass['color']))
    return areaValues, scatter

#_______________________________________________________________________________
def _makeHistogram(key, sizeClass, countLabel):
    df = pd.read_hdf(OUT_PATH, key + 'histogram')
    return plotlyGraph.Bar(
        name='%s (%s)' % (sizeClass['name'], countLabel),
        x=100.0*df['x'],
        y=df['y'],
        marker=plotlyGraph.Marker(color=sizeClass['color']) )

#_______________________________________________________________________________
def plotTraces(
        plotType, label, traces, title, metadata, layoutOptions, suffix =None
):
    suffix = '' if not suffix else ('-' + suffix)

    url = plotly.plot(
        filename=PlotlyUtils.getPlotlyFilename(
            filename='{}{}'.format(label.replace(' ', '-'), suffix),
            folder=PLOTLY_FOLDER),
        figure_or_data=plotlyGraph.Figure(
            data=plotlyGraph.Data(traces),
            layout=_getLayout(
                metadata=metadata,
                title=title, **layoutOptions)),
        auto_open=False)

    print('{}[{}]: {}'.format(plotType, label, PlotlyUtils.toEmbedUrl(url)))

#_______________________________________________________________________________
def plotComparison(label, name, tracks, metadata):

    metadata = metadata[name]
    expectedDf = pd.read_hdf(OUT_PATH, '{}/expected'.format(name))
    areaValues = np.zeros(len(expectedDf['x']) - 1)

    areaTraces = []
    areaPercentageTraces = []
    histTraces = []
    histPercentageTraces = []

    for sizeClass in PlotConfigs.SIZE_CLASSES:
        dataSlice = tracks.query('sizeClass == {}'.format(sizeClass['index']))
        options = {
            'sizeClass': sizeClass,
            'key': '{}/{}/'.format(name, sizeClass['id']),
            'countLabel': locale.format(
                '%d', int(dataSlice.shape[0]), grouping=True)
        }

        histTrace = _makeHistogram(**options)
        histTraces.append(histTrace)

        areaValues, areaTrace = _makeRemainder(
            areaValues=areaValues,
            isFirst=PlotConfigs.SIZE_CLASSES.index(sizeClass) < 1,
            **options)
        areaTraces.append(areaTrace)

    countLabel = locale.format('%d', metadata['count'], grouping=True)

    areaTraces.append(plotlyGraph.Scatter(
        name='Normal Threshold',
        x=100.0*expectedDf['x'],
        y=expectedDf['y'],
        mode='lines',
        line=plotlyGraph.Line(
            color='rgba(0, 0, 0, 0.75)',
            dash='dash',
            width=1.0) ))

    doPlotTraces = functools.partial(
        plotTraces,
        label=label,
        metadata=metadata)

    doPlotTraces(
        plotType='HISTOGRAM',
        traces=histTraces,
        title='Distribution of Track {} Deviations ({} Measurements)'.format(
            label, countLabel),
        layoutOptions={'barmode': 'stack'} )

    doPlotTraces(
        plotType='HIST-LOG',
        suffix='histogram-log',
        traces=histTraces,
        title='Distribution of Track {} Deviations ({} Measurements)'.format(
            label, countLabel),
        layoutOptions={
            'barmode': 'stack',
            'yAxis':{
                'title': 'Frequency (log)',
                'type':'log' }} )

    doPlotTraces(
        plotType='REMAINDER',
        suffix='cdf-remainder',
        traces=areaTraces,
        layoutOptions={'fixed':True},
        title=('Inverse Cumulative Distribution of Track ' +
                    '{} Deviations ({} Tracks)').format(label, countLabel) )

    doPlotTraces(
        plotType='REMAINDER-LOG',
        suffix='cdf-remainder-log',
        traces=areaTraces,
        layoutOptions={
            'fixed':True,
            'yAxis': {
                'title': 'Frequency (log)',
                'type': 'log' }},
        title=('Inverse Cumulative Distribution of Track ' +
                    '{} Deviations ({} Tracks)').format(label, countLabel) )

################################################################################

#_______________________________________________________________________________
def _main_(args):
    tracks = DataLoadUtils.getTrackWithAnalysis()
    with open(METADATA_FILE, 'r') as f:
        metadata = json.loads(f.read())

    doPlot = functools.partial(
        plotComparison,
        tracks=tracks,
        metadata=metadata)

    doPlot(name='width', label='Width')
    doPlot(name='length', label='Length')
    doPlot(name='stride', label='Stride Length')
    doPlot(name='pace', label='Pace Length')

#_______________________________________________________________________________
if __name__ == '__main__':
    from argparse import ArgumentParser
    from textwrap import dedent
    parser = ArgumentParser()

    parser.description = dedent("""
        ValidationPaper does...""")

    _main_(parser.parse_args())

