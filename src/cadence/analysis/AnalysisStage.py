# AnalysisStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import namedtuple

from PyPDF2.merger import PdfFileMerger
from PyPDF2.pdf import PdfFileReader
from pyaid.config.ConfigsDict import ConfigsDict
from pyaid.time.TimeUtils import TimeUtils


try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

#*************************************************************************************************** AnalysisStage
class AnalysisStage(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    VALUE_UNCERTAINTY = namedtuple('VALUE_UNCERTAINTY', ['mean', 'std', 'label'])

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, label =None, **kwargs):
        """Creates a new instance of AnalysisStage."""
        self.owner = owner

        self._key   = key
        self._cache = ConfigsDict()
        self._label = label if label else self.__class__.__name__
        self._startTime = None

        self._analyzeCallback       = kwargs.get('analyze')
        self._preStageCallback      = kwargs.get('pre')
        self._postStageCallback     = kwargs.get('post')
        self._sitemapCallback       = kwargs.get('sitemap')
        self._seriesCallback        = kwargs.get('series')
        self._trackwayCallback      = kwargs.get('trackway')
        self._trackCallback         = kwargs.get('track')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: key
    @property
    def key(self):
        return self._key

#___________________________________________________________________________________________________ GS: index
    @property
    def index(self):
        try:
            return self.owner.stages.index(self)
        except Exception:
            return -1

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        return self._cache

#___________________________________________________________________________________________________ GS: logger
    @property
    def logger(self):
        return self.owner.logger

#___________________________________________________________________________________________________ GS: plot
    @property
    def plot(self):
        return plt

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getPath
    def getPath(self, *args, **kwargs):
        """getPath doc..."""
        return self.owner.getPath(*args, **kwargs)

#___________________________________________________________________________________________________ GS: getTempPath
    def getTempPath(self, *args, **kwargs):
        return self.owner.getTempPath(*args, **kwargs)

#___________________________________________________________________________________________________ analyze
    def analyze(self):
        """analyze doc..."""

        self._startTime = TimeUtils.getNowDatetime()
        self._writeHeader()
        self._preAnalyze()
        self._analyze()
        self._postAnalyze()
        self._writeFooter()

#___________________________________________________________________________________________________ mergePdfs
    def mergePdfs(self, paths, fileName =None):
        """mergePdfs doc..."""

        merger = PdfFileMerger()
        for p in paths:
            merger.append(PdfFileReader(file(p, 'rb')))

        if not fileName:
            fileName = '%s-Report.pdf' % self.__class__.__name__
        merger.write(file(self.getPath(fileName), 'wb'))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _writeHeader
    def _writeHeader(self):
        """_writeHeader doc..."""

        self.logger.write('\n' + 80*'*')
        self.logger.write('\n'.join([
            '[STARTED]: %s ANALYSIS STAGE' % self._label.upper(),
            'Run on %s' % TimeUtils.toZuluFormat(self._startTime).replace('T', ' at ')]
            + self._getHeaderArgs()))

#___________________________________________________________________________________________________ _getHeaderArgs
    # noinspection PyMethodMayBeStatic
    def _getHeaderArgs(self):
        """_getHeaderArgs doc..."""
        return []

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        """_preAnalyze doc..."""
        if self._preStageCallback:
            self._preStageCallback(self)

#___________________________________________________________________________________________________ _analyze
    def _analyze(self):
        """_analyze doc..."""

        if not self._analyzeCallback or self._analyzeCallback(self):
            for sitemap in self.owner.getSitemaps():
                self._analyzeSitemap(sitemap)

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        """_analyze doc..."""

        if self._sitemapCallback and not self._sitemapCallback(self, sitemap):
            return

        for tw in self.owner.getTrackways(sitemap):
            self._analyzeTrackway(tw, sitemap)

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        """_analyzeTrackway doc..."""

        if self._trackwayCallback and not self._trackwayCallback(self, trackway, sitemap):
            return

        for key, series in self.owner.getTrackwaySeries(trackway).items():
            if series.isReady:
                self._analyzeTrackSeries(series, trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        """_analyzeTrackSeries doc..."""

        if self._seriesCallback and not self._seriesCallback(self, series, trackway, sitemap):
            return

        for t in series.tracks:
            self._analyzeTrack(t, series, trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """_analyzeTrack doc..."""
        if self._trackCallback:
            self._trackCallback(self, track, series, trackway, sitemap)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        if self._postStageCallback:
            self._postStageCallback(self)

#___________________________________________________________________________________________________ _writeFooter
    def _writeFooter(self):
        """_writeHeader doc..."""

        elapsed = TimeUtils.getElapsedTime(
            startDateTime=self._startTime,
            endDateTime=TimeUtils.getNowDatetime(),
            toUnit=TimeUtils.MILLISECONDS)

        self.logger.write('\n' + 80*'*')
        self.logger.write('\n'.join([
            '[COMPLETE]: %s ANALYSIS STAGE' % self._label.upper(),
            'Elapsed Time: %s' % TimeUtils.toPrettyElapsedTime(elapsed)] + self._getFooterArgs()))

#___________________________________________________________________________________________________ _getFooterArgs
    # noinspection PyMethodMayBeStatic
    def _getFooterArgs(self):
        """_getHeaderArgs doc..."""
        return []

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

