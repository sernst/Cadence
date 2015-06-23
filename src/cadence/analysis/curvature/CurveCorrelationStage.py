# CurveCorrelationStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

import numpy as np

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.shared.plotting.AutoCorrelationPlot import AutoCorrelationPlot

#*************************************************************************************************** CurveCorrelationStage
class CurveCorrelationStage(CurveOrderedAnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S


#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of CurveCorrelationStage."""
        super(CurveCorrelationStage, self).__init__(
            key, owner,
            label='Curve Correlation',
            **kwargs)

        self._paths = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._paths = []

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):

        trackway.cache.set('curvePoints', {'x':[], 'y':[]})
        super(CurveCorrelationStage, self)._analyzeTrackway(trackway, sitemap)
        data = trackway.cache.extract('curvePoints')

        if len(data['x']) < 2:
            return

        xDelta = 0.05
        xStart = data['x'][0]
        xEnd = data['x'][-1]
        xs = np.linspace(xStart, xEnd, int(math.ceil((xEnd - xStart)/xDelta)))

        signal = self.interpConstant(data, xs)

        plot = AutoCorrelationPlot(
            data=signal['y'],
            title='%s Trackway Phase Auto-Correlation' % trackway.name,
            xLabel='Lag (5cm intervals)',
            yLabel='Auto-Correlation')
        self._paths.append(plot.save(self.getTempFilePath(extension='pdf')))

#___________________________________________________________________________________________________ interpConstant
    @classmethod
    def interpConstant(cls, data, xValues):
        """_interpConstant doc..."""

        index = 0
        out = {'x':[], 'y':[]}

        for xValue in xValues:
            while index < (len(data['x']) - 1) and float(xValue) >= float(data['x'][index + 1]):
                index += 1

            out['x'].append(xValue)
            out['y'].append(data['y'][index])

        return out

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """_analyzeTrack doc..."""

        data = trackway.cache.get('curvePoints')

        analysisTrack = track.getAnalysisPair(self.analysisSession)

        data['x'].append(analysisTrack.curvePosition)

        if track.pes:
            signal = 1 if track.left else -1
        else:
            signal = 2 if track.left else -2

        data['y'].append(signal)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self.mergePdfs(self._paths, 'Phase-Coherence.pdf')
