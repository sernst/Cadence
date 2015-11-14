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
def _getLayout(metadata, title, fixed = False, **kwargs):
    xAxis = plotlyGraph.XAxis(title='Deviation (%)')

    if fixed:
        xAxis['range'] = [
            100.0*metadata['xMin'],
            100.0*min(4.0, metadata['xMax']) ]
        xAxis['autorange'] = False

    return plotlyGraph.Layout(
        title=title,
        xaxis=xAxis,
        yaxis=plotlyGraph.YAxis(
            title='Frequency',
            autorange=True),
        **kwargs)

#_______________________________________________________________________________
def _makeRemainder(key, sizeClass, areaValues, countLabel, color, isFirst):
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
            color=color))
    return areaValues, scatter

#_______________________________________________________________________________
def _makeHistogram(key, sizeClass, color, countLabel):
    df = pd.read_hdf(OUT_PATH, key + 'histogram')
    return plotlyGraph.Bar(
        name='%s (%s)' % (sizeClass['name'], countLabel),
        x=100.0*df['x'],
        y=df['y'],
        marker=plotlyGraph.Marker(color=color) )

#_______________________________________________________________________________
def plotComparison(label, name, tracks, metadata):

    metadata = metadata[name]
    expectedDf = pd.read_hdf(OUT_PATH, '{}/expected'.format(name))
    areaValues = np.zeros(len(expectedDf['x']) - 1)
    areaTraces = []
    histTraces = []

    for sizeClass in PlotConfigs.SIZE_CLASSES:
        color = sizeClass['color']
        key = '{}/{}/'.format(name, sizeClass['id'])
        dataSlice = tracks.query('sizeClass == {}'.format(sizeClass['index']))

        sliceCountLabel = locale.format(
            '%d', int(dataSlice.shape[0]), grouping=True)

        histTrace = _makeHistogram(key, sizeClass, color, sliceCountLabel)
        histTraces.append(histTrace)

        areaValues, areaTrace = _makeRemainder(
            key=key,
            sizeClass=sizeClass,
            areaValues=areaValues,
            countLabel=sliceCountLabel,
            color=color,
            isFirst=PlotConfigs.SIZE_CLASSES.index(sizeClass) < 1)
        areaTraces.append(areaTrace)

    countLabel = locale.format('%d', metadata['count'], grouping=True)

    url = plotly.plot(
        filename=PlotlyUtils.getPlotlyFilename(
            filename='%s' % label.replace(' ', '-'),
            folder=PLOTLY_FOLDER),
        figure_or_data=plotlyGraph.Figure(
            data=plotlyGraph.Data(histTraces),
            layout=_getLayout(
                barmode='stack',
                metadata=metadata,
                title='Distribution of Track {} Deviations ({} Tracks)'.format(
                    label, countLabel ))),
        auto_open=False)

    print(
        'COMPARE|HIST[%s]' % label,
        'x:(%s, %s)' % (metadata['xMin'], metadata['xMax']),
        PlotlyUtils.toEmbedUrl(url))

    areaTraces.append(plotlyGraph.Scatter(
        name='Normal Threshold',
        x=100.0*expectedDf['x'],
        y=expectedDf['y'],
        mode='lines',
        line=plotlyGraph.Line(
            color='rgba(0, 0, 0, 0.75)',
            dash='dash',
            width=1.0) ))

    url = plotly.plot(
        filename=PlotlyUtils.getPlotlyFilename(
            filename='%s-cdf-remainder' % label.replace(' ', '-'),
            folder=PLOTLY_FOLDER),
        figure_or_data=plotlyGraph.Figure(
            data=plotlyGraph.Data(areaTraces),
            layout=_getLayout(
                fixed=True,
                metadata=metadata,
                title=('Inverse Cumulative Distribution of Track ' +
                    '{} Deviations ({} Tracks)').format(label, countLabel))),
        auto_open=False)

    print(
        'COMPARE|AREA[%s]' % label,
        'x:(%s, %s)' % (metadata['xMin'], metadata['xMax']),
        PlotlyUtils.toEmbedUrl(url))

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

