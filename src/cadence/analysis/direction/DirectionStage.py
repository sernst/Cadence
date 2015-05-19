# DirectionStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.StrideLine import StrideLine

from cadence.analysis.shared.PositionValue2D import PositionValue2D
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
        self.trackwaysData[trackway.uid] = []
        super(DirectionStage, self)._analyzeTrackway(trackway, sitemap)

        data = [item['point'] for item in self.trackwaysData[trackway.uid]]

        plot = ScatterPlot(
            data=data,
            title='%s Trackway Angles' % trackway.name,
            yLabel='Angle (Degrees)',
            xLabel='Trackway Curve Position (m)')
        plot.shaveDataToXLimits()
        self._paths.append(plot.save(self.getTempFilePath(extension='pdf')))

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):

        if len(series.tracks) < 2:
            return

        analysisTrack = track.getAnalysisPair(self.analysisSession)
        strideLine = StrideLine(track, series)
        self.trackwaysData[trackway.uid].append({
            'track':track,
            'point':PositionValue2D(
                x=analysisTrack.curvePosition,
                y=strideLine.angle.degrees),
            'angle':strideLine.angle.degrees})

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        self.mergePdfs(self._paths, 'Trackway-Angles')

