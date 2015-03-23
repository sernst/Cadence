# DrawLengthWidthStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage

#*************************************************************************************************** DrawLengthWidthStage
class DrawLengthWidthStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of LengthWidthStage."""
        super(DrawLengthWidthStage, self).__init__(
            key, owner,
            label='Length & Width Map Drawing ',
            **kwargs)
        self._paths = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: trackDeviations
    @property
    def trackDeviations(self):
        return self.owner.getStage('lengthWidth').deviations

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        super(DrawLengthWidthStage, self)._analyzeSitemap(sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        pass
