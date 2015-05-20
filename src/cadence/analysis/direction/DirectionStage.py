# DirectionStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.dict.DictUtils import DictUtils
from pyaid.list.ListUtils import ListUtils

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.StrideLine import StrideLine

from cadence.analysis.shared.PositionValue2D import PositionValue2D
from cadence.analysis.shared.plotting.BarPlot import BarPlot
from cadence.analysis.shared.plotting.Histogram import Histogram
from cadence.analysis.shared.plotting.MultiScatterPlot import MultiScatterPlot
from cadence.analysis.shared.plotting.ScatterPlot import ScatterPlot

#*************************************************************************************************** DirectionStage
class DirectionStage(CurveOrderedAnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of DirectionStage."""
        super(DirectionStage, self).__init__(
            key, owner,
            label='Trackway Angles',
            **kwargs)
        self._paths  = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: trackwaysData
    @property
    def trackwaysData(self):
        return self.cache.get('trackwaysData')

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self.cache.set('trackwaysData', {})

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackway(self, trackway, sitemap):
        entries = []
        data = {'entries':entries}

        self.trackwaysData[trackway.uid] = data
        super(DirectionStage, self)._analyzeTrackway(trackway, sitemap)

        if len(entries) < 2:
            del self.trackwaysData[trackway.uid]
            return

        d = [item['deviation'] for item in entries]

        significantDeviations = []
        for deviation in d:
            if deviation >= 1.0:
                significantDeviations.append(deviation)

        devs = {
            'global':d[-1],
            'max':max(*d),
            'fraction':len(significantDeviations)/len(d) }

        data['deviations'] = devs

        color = 'blue'
        if devs['global'] >= 1.0:
            color = 'red'
        elif devs['max'] >= 1.0:
            color ='green'

        d = [item['point'] for item in entries]
        plot = ScatterPlot(
            data=d,
            color=color,
            title='%s Trackway Angles' % trackway.name,
            yLabel='Angle (Degrees)',
            xLabel='Trackway Curve Position (m)')
        self._paths.append(plot.save(self.getTempFilePath(extension='pdf')))

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):

        if len(series.tracks) < 2:
            return

        analysisTrack = track.getAnalysisPair(self.analysisSession)
        strideLine = StrideLine(track, series)
        data = self.trackwaysData[trackway.uid]['entries']

        angle = strideLine.line.angle
        deviation = 0.0

        if len(data) > 0:
            referenceAngle = data[0]['angle']
            denom = abs(referenceAngle.uncertainty) + abs(angle.uncertainty)
            deviation = abs(angle.radians - referenceAngle.radians)/denom

        data.append({
            'track':track,
            'deviation':deviation,
            'point':PositionValue2D(
                x=analysisTrack.curvePosition,
                y=strideLine.angle.degrees,
                yUnc=angle.uncertaintyDegrees),
            'angle':angle})

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""

        self._processCurveDeviations('max', 'Meandering')
        self._processCurveDeviations('global', 'Globally Curved')

        d = [100.0*data['deviations']['fraction'] for k, data in DictUtils.iter(self.trackwaysData)]
        d.sort()

        plot = BarPlot(
            data=d,
            title='Significant Deviations from Reference',
            yLabel='Fraction of Deviations (%)',
            xLabel='Trackway Index')
        self._paths.insert(0, plot.save(self.getTempFilePath(extension='pdf')))

        self.mergePdfs(self._paths, 'Trackway-Angles')

#___________________________________________________________________________________________________ _processCurveDeviations
    def _processCurveDeviations(self, key, label):
        """_processCurveDeviations doc..."""

        d = [data['deviations'][key] for k, data in DictUtils.iter(self.trackwaysData)]
        dCurved = []
        dStraight = []
        for item in d:
            if item < 1.0:
                dStraight.append(item)
            else:
                dCurved.append(min(10.0, item))

        plot = Histogram(
            data=dCurved,
            title='%s Trackway Deviations' % label,
            xLabel='Trackway Index')
        self._paths.insert(0, plot.save(self.getTempFilePath(extension='pdf')))

        d = [(index, d[index]) for index in ListUtils.rangeOn(d)]
        dCurved = []
        dStraight = []
        for item in d:
            if item[-1] < 1.0:
                dStraight.append(item)
            else:
                dCurved.append((item[0], min(10.0, item[1])) )

        self.logger.write('%s Trackways: %s/%s (%s%%)' % (
            label,
            len(dCurved),
            len(dCurved) + len(dStraight),
            100.0*len(dCurved)/(len(dCurved) + len(dStraight)) ))

        plot = MultiScatterPlot(
            {'data':dStraight, 'color':'blue'},
            {'data':dCurved, 'color':'red'},
            title='%s Trackway Deviations' % label,
            xLabel='Trackway Index',
            yLabel='Fractional Deviation')
        self._paths.insert(1, plot.save(self.getTempFilePath(extension='pdf')))
