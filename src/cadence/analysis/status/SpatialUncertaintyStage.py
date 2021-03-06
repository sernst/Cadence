# SpatialUncertaintyStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.analysis.shared.plotting.Histogram import Histogram
from cadence.svg.CadenceDrawing import CadenceDrawing

#*************************************************************************************************** SpatialUncertaintyStage
class SpatialUncertaintyStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    DRAWING_FOLDER_NAME = 'Spatial-Unc-Maps'

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of SpatialUncertaintyStage."""
        super(SpatialUncertaintyStage, self).__init__(
            key, owner,
            label='Spatial Uncertainty',
            **kwargs)

        self._uncs        = []
        self._largeUncCsv = None
        self._tracks      = []

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _preAnalyze(self):
        self._uncs   = []
        self._tracks = []

        self.initializeFolder(self.DRAWING_FOLDER_NAME)

        csv = CsvWriter()
        csv.path = self.getPath('Large-Spatial-Uncertainties.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('x', 'X'),
            ('z', 'Z') )
        self._largeUncCsv = csv

#_______________________________________________________________________________
    def _analyzeTrack(self, track, series, trackway, sitemap):
        trackId = '%s (%s)' % (track.fingerprint, track.uid)

        if NumericUtils.equivalent(track.width, 0.0):
            self.logger.write('[ERROR]: Zero track width %s' % trackId)
        if NumericUtils.equivalent(track.widthUncertainty, 0.0):
            self.logger.write('[ERROR]: Zero track width uncertainty %s' % trackId)

        if NumericUtils.equivalent(track.length, 0.0):
            self.logger.write('[ERROR]: Zero track length %s' % trackId)
        if NumericUtils.equivalent(track.lengthUncertainty, 0.0):
            self.logger.write('[ERROR]: Zero track length uncertainty %s' % trackId)

        self._tracks.append(track)
        x = track.xValue
        self._uncs.append(x.uncertainty)
        z = track.zValue
        self._uncs.append(z.uncertainty)

#_______________________________________________________________________________
    def _postAnalyze(self):
        h = Histogram(
            data=self._uncs,
            binCount=80,
            xLimits=(0, max(*self._uncs)),
            color='r',
            title='Distribution of Spatial (X, Z) Uncertainties',
            xLabel='Uncertainty Value (m)',
            yLabel='Frequency')
        p1 = h.save(self.getTempFilePath(extension='pdf'))

        h.isLog = True
        h.title += ' (log)'
        p2 = h.save(self.getTempFilePath(extension='pdf'))

        self.mergePdfs([p1, p2], self.getPath('Spatial-Uncertainty-Distribution.pdf'))

        average = NumericUtils.getMeanAndDeviation(self._uncs)
        self.logger.write('Average spatial uncertainty: %s' % average.label)

        #-------------------------------------------------------------------------------------------
        # FIND LARGE UNCERTAINTY TRACKS
        largeUncertaintyCount = 0
        drawing = None
        sitemap = None

        # If track uncertainty is 2x average, add that track to the spreadsheet and map overlay
        for t in self._tracks:

            # if the tracksite has changed, save previous map and make a new one
            if sitemap != t.trackSeries.trackway.sitemap:

                # save the last site map drawing (if there was one)
                if drawing:
                    drawing.save()

                # then start a new drawing for this new site map
                sitemap = t.trackSeries.trackway.sitemap

                fileName = sitemap.name + "_" + sitemap.level + '_uncertainty.svg'
                path = self.getPath(self.DRAWING_FOLDER_NAME, fileName, isFile=True)
                drawing = CadenceDrawing(path, sitemap)

                # create a group to be instanced for the spreadsheet values
                drawing.createGroup('rect1')
                # create a rectangle of 100x100 cm that is to be scaled by fractional meters
                drawing.rect((0, 0), 100, 100, scene=True, groupId='rect1')

                # create another group to be instanced for the mapped values.
                drawing.createGroup('rect2')
                # create a rectangle of 100x100 cm that is to be scaled by fractional meters
                drawing.rect((0, 0), 100, 100, scene=True, groupId='rect2')

                # and place a grid and the federal coordinates in the drawing file
                drawing.grid()
                drawing.federalCoordinates()

            # now examine the positional uncertainties for this track
            x = t.xValue
            z = t.zValue

            if x.uncertainty > 0.15 or z.uncertainty > 0.15:
                # s = '%s%s %s%s: %s %s'% (
                #     t.site, t.level, t.trackwayType, t.trackwayNumber, t.name, t.uid)
                # print('%s:  (%s and %s)' % (s, x.uncertainty, z.uncertainty))
                print('%s\t%s' % (t.uid, t.fingerprint))

            if max(x.uncertainty, z.uncertainty) <= 2.0*average.uncertainty:
                # then just indicate that this track has low uncertainty
                self._drawLowUncertaintyMarker(drawing, t)
                # label this track with green
                drawing.text(
                    t.name,
                    (t.x - 20, t.z),
                    scene=True,
                    stroke='green',
                    stroke_width='0.25',
                    font_size='8px',
                    font_family='Arial')
                continue

            # else, since the uncertainty is high, first write that track in the spreadsheet
            largeUncertaintyCount += 1
            self._largeUncCsv.createRow(
                uid=t.uid,
                fingerprint=t.fingerprint,
                x=x.label,
                z=z.label)

            # if either the measured width or length is 0, mark with a yellow disk with red outline
            if t.widthMeasured == 0 or t.lengthMeasured == 0:
                drawing.circle(
                    (t.x, t.z),
                    100*(t.widthUncertainty + t.lengthUncertainty)/2.0,
                    scene=True,
                    fill='yellow',
                    stroke='red')
                drawing.text(
                    t.name,
                    (t.x - 20, t.z),
                    scene=True,
                    stroke='black',
                    stroke_width='0.25',
                    font_size='6px',
                    font_family='Arial')
                continue

            self._drawHighUncertaintyMarker(drawing, t)

            # label this track with red
            drawing.text(
                t.name,
                (t.x - 20, t.z),
                scene=True,
                stroke='red',
                stroke_width='0.25',
                font_size='6px',
                font_family='Arial')
#
#             # draw this track indicating it has high uncertainty
#             drawing.use(
#                     'rect1',
#                     (t.x, t.z),
#                     scene=True,
#                     rotation=t.rotation,
#                     opacity='0.5',
#                     scale=t.widthMeasured,
#                     scaleY=t.lengthMeasured,
#                     fill='red',
#                     stroke='red')
#
#             # draw the map dimensions with an outline gray rectangle
#             drawing.use(
#                     'rect2',
#                     (t.x, t.z),
#                     scene=True,
#                     rotation=t.rotation,
#                     scale=t.width,
#                     scaleY=t.length,
#                     fill='none',
#                     stroke='gray')

        # and close off with a final save of the drawing file
        if drawing:
            drawing.save()


        self.logger.write('%s Tracks with large spatial uncertainties found (%s%%)' % (
            largeUncertaintyCount, NumericUtils.roundToOrder(
                100.0*float(largeUncertaintyCount)/float(len(self._tracks)), -1) ))

        self._largeUncCsv.save()
        self._tracks = []

#_______________________________________________________________________________
    @classmethod
    def _drawLowUncertaintyMarker(cls, drawing, track):
        """ Indicate a low-uncertainty track at the specified location.  The radius is the average
            of width and length uncertainty. """

        r = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0
        drawing.circle(
            (track.x, track.z),
            r,
            scene=True,
            fill='green',
            stroke='green')

#_______________________________________________________________________________
    @classmethod
    def _drawHighUncertaintyMarker(cls, drawing, track):
        """ Indicate a low-uncertainty track at the specified location.  Radius is average
            uncertainty """

        drawing.circle(
            (track.x, track.z),
            100*(track.widthUncertainty + track.lengthUncertainty)/2.0,
            scene=True,
            fill='red',
            stroke='red')
