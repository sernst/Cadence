# CurveProjectionStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.dict.DictUtils import DictUtils
from pyaid.list.ListUtils import ListUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.curvature.CurveSeries import CurveSeries
from cadence.analysis.shared.plotting.Histogram import Histogram
from cadence.svg.CadenceDrawing import CadenceDrawing

#*************************************************************************************************** CurveProjectionStage
class CurveProjectionStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    CURVE_MAP_FOLDER_NAME = 'Projection-Maps'

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of CurveProjectionStage."""
        super(CurveProjectionStage, self).__init__(
            key, owner,
            label='Curve Projection',
            **kwargs)

        self._paths = []

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def data(self):
        return self.cache.getOrAssign('data', {})

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _preAnalyze(self):
        self._paths = []

        self.initializeFolder(self.CURVE_MAP_FOLDER_NAME)

#_______________________________________________________________________________
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""

        self._createDrawing(sitemap, 'PROJECTION', self.CURVE_MAP_FOLDER_NAME)
        super(CurveProjectionStage, self)._analyzeSitemap(sitemap)
        self._saveDrawing(sitemap)

#_______________________________________________________________________________
    def _analyzeTrackway(self, trackway, sitemap):

        analysisTrackway = trackway.getAnalysisPair(self.analysisSession)
        if not analysisTrackway or not analysisTrackway.curveSeries:
            # Ignore trackways that are too short to have a curve series
            return

        # Fetch the curve series from the analysisTrackway.curveSeries value
        curveSeries = None
        bundle = self.owner.getSeriesBundle(trackway)
        for value in bundle.asList():
            if value.firstTrackUid == analysisTrackway.curveSeries:
                curveSeries = value
                break

        if not curveSeries:
            # Abort if no curve series was found. This should only occur if the there's a data
            # corruption between the Tracks_Trackway table and the Analysis_Trackway.curveSeries
            # value.
            self.logger.write([
                '[ERROR]: No curve series found',
                'TRACKWAY[%s]: %s' % (trackway.index, trackway.name),
                'CURVE_SERIES: %s' % analysisTrackway.curveSeries])
            return

        curve = CurveSeries(stage=self, series=curveSeries, saveToAnalysisTracks=True)

        try:
            curve.compute()
        except ZeroDivisionError as err:
            self.logger.writeError([
                '[ERROR]: Failed to compute curve series',
                'TRACKWAY: %s' % trackway.name,
                'SITEMAP: %s' % sitemap.name], err)
            raise

        self.data[trackway.uid] = curve
        for error in curve.errors:
            self.logger.write(error)
        curve.draw(sitemap.cache.get('drawing'))
        #print(curve.getDebugReport())

#_______________________________________________________________________________
    def _postAnalyze(self):
        """_postAnalyze doc..."""

        ratios = []

        for name, curve in DictUtils.iter(self.data):
            segments = curve.segments

            for i in ListUtils.rangeOn(segments):
                segment = segments[i]
                segmentLine = segment.line

                # If this is an extrapolated segment, use the length from the neighboring segment
                # instead of the artificial length of this segment.
                if segment == segments[0]:
                    segmentLine = segments[i + 1].line
                elif segment == segments[-1]:
                    segmentLine = segments[i - 1].line

                for pairData in segment.pairs:
                    projectionLine = pairData['line']
                    ratios.append(100.0*projectionLine.length.raw/segmentLine.length.raw)

        h = Histogram(
            data=ratios,
            binCount=50,
            xLabel='Projection/Stride Ratio (%)',
            title='Relative Stride to Projection Length Ratios')
        h.shaveDataToXLimits()
        self._paths.append(h.save(path=self.getTempFilePath(extension='pdf')))

        self.mergePdfs(self._paths, 'Curve-Projection.pdf')
