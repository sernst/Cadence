# TrackwayDeflectionStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.svg.CadenceDrawing import CadenceDrawing

#*************************************************************************************************** TrackwayDeflectionStage
class TrackwayDeflectionStage(CurveOrderedAnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    MAPS_FOLDER_NAME = 'Trackway-Deflection'

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayDeflectionStage."""
        super(TrackwayDeflectionStage, self).__init__(
            key, owner,
            label='Trackway Deflection',
            **kwargs)
        self._paths = []

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def trackwayDirectionData(self):
        return self.owner.getStage('direction').trackwayDirectionData

#_______________________________________________________________________________
    @property
    def trackwayDeflectionData(self):
        return self.owner.cache.get('trackwayDeflectionData')

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _preAnalyze(self):
        self.owner.cache.set('trackwayDeflectionData', {})

#_______________________________________________________________________________
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""

        drawing = CadenceDrawing(
            self.getPath(
                self.MAPS_FOLDER_NAME,
                '%s-%s-DEFLECTION.svg' % (sitemap.name, sitemap.level),
                isFile=True),
            sitemap)

        drawing.grid()
        drawing.federalCoordinates()
        sitemap.cache.set('drawing', drawing)

        super(TrackwayDeflectionStage, self)._analyzeSitemap(sitemap)

        try:
            sitemap.cache.extract('drawing').save()
        except Exception:
            self.logger.write('[WARNING]: No sitemap saved for %s-%s' % (
                sitemap.name, sitemap.level))

#_______________________________________________________________________________
    def _analyzeTrackway(self, trackway, sitemap):
        if trackway.uid not in self.trackwayDirectionData:
            return

        # TODO: Analyze deflections for each trackway

#===============================================================================
#                                                                               I N T R I N S I C

#_______________________________________________________________________________
    def __repr__(self):
        return self.__str__()

#_______________________________________________________________________________
    def __str__(self):
        return '<%s>' % self.__class__.__name__

