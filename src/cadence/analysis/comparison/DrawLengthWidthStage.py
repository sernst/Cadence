# DrawLengthWidthStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage

from cadence.svg.CadenceDrawing import CadenceDrawing

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

        self._currentDrawing = None

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

         # get ready for a new drawing
        fileName = sitemap.name + "_" + sitemap.level + '_lengthWidth.svg'
        path     = self.getPath(self.DRAWING_FOLDER_NAME, fileName, isFile=True)

        self._currentDrawing = CadenceDrawing(path, sitemap)

        # create a bar-shaped pointer for map annotation
        self._currentDrawing.createGroup('bar')
        self._currentDrawing.line((0, 0), (0, -20), scene=False, groupId='bar')

        # and place a grid and the federal coordinates in the drawing file
        self._currentDrawing.grid()
        self._currentDrawing.federalCoordinates()

        # do what needs to be done
        super(DrawLengthWidthStage, self)._analyzeSitemap(sitemap)

        # then when back, save the drawing
        if self._currentDrawing:
            self._currentDrawing.save()

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):

        # visualize track width and length compared to measured values for these dimensions
        self.drawTrack(track)

#___________________________________________________________________________________________________ drawTrack
    def drawTrack(self, track):
        """ The dimensions of a given track is drawn, and added to a given drawing, using the given
            CadenceDrawing group (a line oriented with the SVG positive Y direction. """

        # if the lengthMeasured is non-zero, render it either red or green, depending on deviation
        if track.lengthMeasured != 0.0:
            if track.uid in self.trackDeviations:
                data = self.trackDeviations[track.uid]
                if data['lSigma'] > 2.0:
                      strokeWidth = 3.0
                      color       = 'red'
                else:
                    strokeWidth = 1.0
                    color = 'green'
            else:
                strokeWidth = 1.0
                color       = 'green'

            if not self._currentDrawing:
                return

            self._currentDrawing.use(
                'bar',
                (track.x, track.z),
                scale=1.0,
                scaleY=track.lengthRatio*track.lengthMeasured,
                rotation=track.rotation,
                scene=True,
                stroke=color,
                stroke_width=strokeWidth)
            self._currentDrawing.use(
                'bar',
                (track.x, track.z),
                scale=1.0,
                scaleY=(1.0 - track.lengthRatio)*track.lengthMeasured,
                rotation=track.rotation + 180.0,
                scene=True,
                stroke=color,
                stroke_width=strokeWidth)

        # and likewise for widthMeasured (if non-zero and deviation is significant)
        if  track.widthMeasured != 0.0:
            if track.uid in self.trackDeviations:
                data = self.trackDeviations[track.uid]
                if data['wSigma'] > 2.0:
                    strokeWidth = 3.0
                    color       = 'red'
                else:
                    strokeWidth = 1.0
                    color = 'green'
            else:
                strokeWidth = 1.0
                color       = 'green'

            if not self._currentDrawing:
                return

            self._currentDrawing.use(
                'bar',
                (track.x, track.z),
                scale=2.0,
                scaleY=track.widthMeasured/2.0,
                rotation=track.rotation + 90.0,
                scene=True,
                stroke=color,
                stroke_width=strokeWidth)
            self._currentDrawing.use(
                'bar',
                (track.x, track.z),
                scale=2.0,
                scaleY=track.widthMeasured/2.0,
                rotation=track.rotation - 90.0,
                scene=True,
                stroke=color,
                stroke_width=strokeWidth)

        if not self._currentDrawing:
           print('Ha! in draw track, track = %s' % track)
           return

        # now overlay onto the above measured-dimension bars the corresponding length indicators
        self._currentDrawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=track.lengthRatio*track.length,
            rotation=track.rotation,
            scene=True,
            stroke='yellow',
            stroke_width=0.5)

        # draw the remaining portion of the length bar
        self._currentDrawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=(1.0 - track.lengthRatio)*track.length,
            rotation=track.rotation + 180.0,
            scene=True,
            stroke='yellow',
            stroke_width=0.5)

        # and draw a bar representing the width (first drawing that part to the right of center)
        self._currentDrawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=track.width/2.0,
            rotation=track.rotation + 90.0,
            scene=True,
            stroke='yellow',
            stroke_width=0.5)

        # then drawing the other part of the width bar that is to the left of center
        self._currentDrawing.use(
            'bar',
            (track.x, track.z),
            scale=1.0,
            scaleY=track.width/2.0,
            rotation=track.rotation - 90.0,
            scene=True,
            stroke='yellow',
            stroke_width=0.5)

