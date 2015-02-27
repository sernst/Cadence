# SpatialUncertaintyStage.py
# (C)2014
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

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of SpatialUncertaintyStage."""
        super(SpatialUncertaintyStage, self).__init__(
            key, owner,
            label='Spatial Uncertainty',
            **kwargs)

        self._uncs        = []
        self._largeUncCsv = None
        self._tracks      = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._uncs = []
        self._tracks = []

        csv = CsvWriter()
        csv.path = self.getPath('Large-Spatial-Uncertainties.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('x', 'X'),
            ('z', 'Z') )
        self._largeUncCsv = csv

#___________________________________________________________________________________________________ _anal
    def _analyzeTrack(self, track, series, trackway, sitemap):
        self._tracks.append(track)
        x = track.xValue
        self._uncs.append(x.uncertainty)
        z = track.zValue
        self._uncs.append(z.uncertainty)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        h = Histogram(
            data=self._uncs,
            binCount=40,
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

            # if the tracksite has changed from the previous track, save previous map
            if sitemap != t.trackSeries.trackway.sitemap:

                # save the last site map drawing, if there was one
                if drawing:
                    drawing.save()

                # then start a new drawing for this new site map
                sitemap = t.trackSeries.trackway.sitemap
                fileName = sitemap + "_largeUncertainty"
                path = self.getPath(fileName)
                drawing = CadenceDrawing(path, sitemap)

                # and place a grid and the federal coordinates in the drawing file
                drawing.grid()
                drawing.federalCoordinates()

            # now examine the positional uncertainties for this track
            x = t.xValue
            z = t.zValue
            if max(x.uncertainty, z.uncertainty) <= 2.0*average.uncertainty:

                # then just indicate that this track has low uncertainty
                self._drawLowUncertaintyMarker(drawing, t)
                continue

            # since the uncertainty is high, first write that track in the spreadsheet
            largeUncertaintyCount += 1
            self._largeUncCsv.createRow(
                uid=t.uid,
                fingerprint=t.fingerprint,
                x=x.label,
                z=z.label)

            # then draw this track in the Cadence drawing indicating it has high uncertainty
            self._drawHighUncertaintyMarker(drawing, t)

        # and close off with a final save of the drawing file
        if drawing:
            drawing.save()


        self.logger.write('%s Tracks with large spatial uncertainties found (%s%%)' % (
            largeUncertaintyCount, NumericUtils.roundToOrder(
                100.0*float(largeUncertaintyCount)/float(len(self._tracks)), -1) ))

        self._largeUncCsv.save()
        self._tracks = []

#___________________________________________________________________________________________________ _drawLowUncertaintyMarker
    def _drawLowUncertaintyMarker(self, drawing, track):
        """ Indicate a low-uncertainty track at the specified location. """

        r = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0
        drawing.circle(
            (track.x, track.z),
            r,
            scene=True,
            fill='green',
            stroke='green')

#___________________________________________________________________________________________________ _drawHighUncertaintyMarker
    def _drawHighUncertaintyMarker(self, drawing, track):
        """ Indicate a low-uncertainty track at the specified location. """

        r = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0
        drawing.circle(
            (track.x, track.z),
            r,
            scene=True,
            fill='red',
            stroke='red')