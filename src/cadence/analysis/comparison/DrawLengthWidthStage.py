# DrawLengthWidthStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage

#*************************************************************************************************** DrawLengthWidthStage
class DrawLengthWidthStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    DRAWING_FOLDER_NAME = 'Spatial-Comparison-Maps'

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of LengthWidthStage."""

        super(DrawLengthWidthStage, self).__init__(
            key, owner,
            label='Length & Width Map Drawing',
            **kwargs)
        self._paths = []

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def trackDeviations(self):
        """ This returns a dictionary of deviation data: track uid, wSigma, and lSigma. """
        return self.owner.getStage('lengthWidth').trackDeviations

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _analyzeSitemap(self, sitemap):
        """ This sets up the Cadence drawing for this current sitemap. """

        drawing = self._createDrawing(sitemap, 'LENGTH-WIDTH', self.DRAWING_FOLDER_NAME)

        # create a bar-shaped pointer for map annotation
        drawing.createGroup('bar')
        drawing.line((0, 0), (0, -20), scene=False, groupId='bar')

        super(DrawLengthWidthStage, self)._analyzeSitemap(sitemap)
        self._saveDrawing(sitemap)

#_______________________________________________________________________________
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """ The dimensions of a given track is drawn, and added to a given drawing, using the given
            CadenceDrawing group (a line oriented with the SVG positive Y direction. """

        drawing = sitemap.cache.get('drawing')
        if not drawing:
           self.logger.write('[WARNING]: No drawing to draw track %s' % track.fingerprint)
           return

        self._drawMeasuredLength(track, drawing)
        self._drawMeasuredWidth(track, drawing)
        self._drawLength(track, drawing)
        self._drawWidth(track, drawing)

#_______________________________________________________________________________
    def _drawMeasuredLength(self, track, drawing):
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

        l   = 100*track.lengthMeasured
        rot = math.radians(track.rotation)
        z1  = track.lengthRatio*l
        z2  = z1 - l

        drawing.line(
             (track.x + z1*math.sin(rot), track.z + z1*math.cos(rot)),
             (track.x + z2*math.sin(rot), track.z + z2*math.cos(rot)),
             scene=True,
             stroke=color,
             stroke_width=strokeWidth)

#_______________________________________________________________________________
    def _drawMeasuredWidth(self, track, drawing):
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

        w   = 100*track.widthMeasured
        rot = math.radians(track.rotation)
        x1  = w/2.0
        x2  = -w/2.0

        drawing.line(
             (track.x + x1*math.cos(rot), track.z - x1*math.sin(rot)),
             (track.x + x2*math.cos(rot), track.z - x2*math.sin(rot)),
             scene=True,
             stroke=color,
             stroke_width=strokeWidth)

#_______________________________________________________________________________
    def _drawLength(self, track, drawing, color ='orange', strokeWidth =0.5):
        if NumericUtils.equivalent(track.lengthMeasured, 0.0):
            return

        l   = 100*track.length
        rot = math.radians(track.rotation)
        z1  = track.lengthRatio*l
        z2  = z1 - l

        # draw the length line
        drawing.line(
             (track.x + z1*math.sin(rot), track.z + z1*math.cos(rot)),
             (track.x + z2*math.sin(rot), track.z + z2*math.cos(rot)),
             scene=True,
             stroke=color,
             stroke_width=strokeWidth)

#_______________________________________________________________________________
    def _drawWidth(self, track, drawing, color ='orange', strokeWidth =0.5):
        if NumericUtils.equivalent(track.widthMeasured, 0.0):
            return

        w   = 100*track.width
        rot = math.radians(track.rotation)
        x1  = w/2.0
        x2  = -w/2.0

        drawing.line(
             (track.x + x1*math.cos(rot), track.z - x1*math.sin(rot)),
             (track.x + x2*math.cos(rot), track.z - x2*math.sin(rot)),
             scene=True,
             stroke=color,
             stroke_width=strokeWidth)
