# DrawLengthWidthStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage

#*************************************************************************************************** DrawLengthWidthStage
class DrawLengthWidthStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    DRAWING_FOLDER_NAME = 'Spatial-Comparison-Maps'

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of LengthWidthStage."""

        super(DrawLengthWidthStage, self).__init__(
            key, owner,
            label='Length & Width Map Drawing',
            **kwargs)
        self._paths = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: trackDeviations
    @property
    def trackDeviations(self):
        """ This returns a dictionary of deviation data: track uid, wSigma, and lSigma. """
        return self.owner.getStage('lengthWidth').trackDeviations

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        """ This sets up the Cadence drawing for this current sitemap. """

        drawing = self._createDrawing(sitemap, 'LENGTH-WIDTH', self.DRAWING_FOLDER_NAME)

        # create a bar-shaped pointer for map annotation
        drawing.createGroup('bar')
        drawing.line((0, 0), (0, -20), scene=False, groupId='bar')

        super(DrawLengthWidthStage, self)._analyzeSitemap(sitemap)
        self._saveDrawing(sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """ The dimensions of a given track is drawn, and added to a given drawing, using the given
            CadenceDrawing group (a line oriented with the SVG positive Y direction. """

        drawing = sitemap.cache.get('drawing')
        if not drawing:
           self.logger.write('[WARNING]: No drawing to draw track %s' % track.fingerprint)
           return

        self._drawLength(track, drawing)
        self._drawWidth(track, drawing)
        self._drawOverlay(track, drawing)

#___________________________________________________________________________________________________ _drawLength
    def _drawLength(self, track, drawing):
        if NumericUtils.equivalent(track.lengthMeasured, 0.0):
            return

        if track.uid in self.trackDeviations:
            data = self.trackDeviations[track.uid]
            if data['lSigma'] > 2.0:
                  strokeWidth = 3.0
                  color = 'red'
            else:
                strokeWidth = 1.0
                color = 'green'
        else:
            strokeWidth = 1.0
            color = 'green'

        drawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=track.lengthRatio*track.lengthMeasured,
            rotation=track.rotation,
            scene=True,
            stroke=color,
            stroke_width=strokeWidth)

        drawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=(1.0 - track.lengthRatio)*track.lengthMeasured,
            rotation=track.rotation + 180.0,
            scene=True,
            stroke=color,
            stroke_width=strokeWidth)

#___________________________________________________________________________________________________ _drawWidth
    def _drawWidth(self, track, drawing):
        if NumericUtils.equivalent(track.widthMeasured, 0.0):
            return

        if track.uid in self.trackDeviations:
            data = self.trackDeviations[track.uid]
            if data['wSigma'] > 2.0:
                strokeWidth = 3.0
                color = 'red'
            else:
                strokeWidth = 1.0
                color = 'green'
        else:
            strokeWidth = 1.0
            color = 'green'

        drawing.use(
            'bar',
            (track.x, track.z),
            scale=2.0,
            scaleY=track.widthMeasured/2.0,
            rotation=track.rotation + 90.0,
            scene=True,
            stroke=color,
            stroke_width=strokeWidth)

        drawing.use(
            'bar',
            (track.x, track.z),
            scale=2.0,
            scaleY=track.widthMeasured/2.0,
            rotation=track.rotation - 90.0,
            scene=True,
            stroke=color,
            stroke_width=strokeWidth)

#___________________________________________________________________________________________________ _drawOverlay
    @classmethod
    def _drawOverlay(cls, track, drawing, color ='orange'):

        # now overlay onto the above measured-dimension bars the corresponding length indicators
        drawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=track.lengthRatio*track.length,
            rotation=track.rotation,
            scene=True,
            stroke=color,
            stroke_width=0.5)

        # draw the remaining portion of the length bar
        drawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=(1.0 - track.lengthRatio)*track.length,
            rotation=track.rotation + 180.0,
            scene=True,
            stroke=color,
            stroke_width=0.5)

        # and draw a bar representing the width (first drawing that part to the right of center)
        drawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=track.width/2.0,
            rotation=track.rotation + 90.0,
            scene=True,
            stroke=color,
            stroke_width=0.5)

        # then drawing the other part of the width bar that is to the left of center
        drawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=track.width/2.0,
            rotation=track.rotation - 90.0,
            scene=True,
            stroke=color,
            stroke_width=0.5)

