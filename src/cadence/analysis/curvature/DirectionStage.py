# DirectionStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.StrideLine import StrideLine
from cadence.util.math2D.Vector2D import Vector2D

#*************************************************************************************************** DirectionStage
class DirectionStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of DirectionStage."""
        super(DirectionStage, self).__init__(
            key, owner,
            label='Track Direction',
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

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        entries = []
        self.cache.set('sitemapData', entries)
        super(DirectionStage, self)._analyzeSitemap(sitemap)

        if not entries:
            return

        average = NumericUtils.weightedAverage(*entries)
        print('>>> SITEMAP[%s]: %s' % (sitemap.name, average.label))

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackway(self, trackway, sitemap):
        self.cache.set('currentTrackway', [])
        super(DirectionStage, self)._analyzeTrackway(trackway, sitemap)

        angles = self.cache.extract('currentTrackway', [])
        if not angles:
            return

        self.trackwaysData[trackway.uid] = {
            'trackway':trackway,
            'angles':angles }

        direction = NumericUtils.getMeanAndDeviation(angles)
        if direction.uncertainty == 0:
            direction = NumericUtils.toValueUncertainty(direction.value, 180.0)
        self.logger.write('%s: %s' % (trackway.name,  direction.label))

        self.cache.get('sitemapData').append(direction)

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        """_analyzeTrackSeries doc..."""

        if len(series.tracks) < 2:
            return

        absoluteAxis = Vector2D(1, 0)
        absoluteAxis.normalize()

        angles = self.cache.get('currentTrackway')
        for track in series.tracks:
            strideLine = StrideLine(track, series)
            angles.append(strideLine.angle.degrees)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        pass

