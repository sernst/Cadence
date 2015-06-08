# AnalysisStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os

from PyPDF2.merger import PdfFileMerger
from PyPDF2.pdf import PdfFileReader
from pyaid.config.ConfigsDict import ConfigsDict
from pyaid.string.StringUtils import StringUtils
from pyaid.system.SystemUtils import SystemUtils
from pyaid.time.TimeUtils import TimeUtils
from cadence.analysis.AnalyzerBase import AnalyzerBase

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

#*************************************************************************************************** AnalysisStage
class AnalysisStage(object):
    """ The base class for creating analysis stages, which are distinct pieces of analysis carried
        out within the scope of an AnalyzerBase instance that owns the stage. """

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, label =None, **kwargs):
        """Creates a new instance of AnalysisStage.

            @type owner: AnalyzerBase """

        # The analyzer that owns this stage
        self.owner = owner

        self._key   = key
        self._cache = ConfigsDict()
        self._label = label if label else self.__class__.__name__
        self._startTime = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: key
    @property
    def key(self):
        """ The identification key for this analyzer stage, which is how the AnalyzerBase
            references this stage. """
        return self._key

#___________________________________________________________________________________________________ GS: index
    @property
    def index(self):
        """ The integer index of this stage within its AnalyzerBase owner. """
        try:
            return self.owner.stages.index(self)
        except Exception:
            return -1

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        """ A DataCache instance used to easily store dynamic key-based data during the analysis
            process. """
        return self._cache

#___________________________________________________________________________________________________ GS: logger
    @property
    def logger(self):
        """ The Logger instance for writing all analysis process information. This logger
            instance is owned by the AnalyzerBase and shared across stages. """
        return self.owner.logger

#___________________________________________________________________________________________________ GS: plot
    @property
    def plot(self):
        """ A convenience reference to Matplotlib's PyPlot module. Included here so Analyzers do
            not have to handle failed Matplotlib loading internally. """
        return plt

#___________________________________________________________________________________________________ GS: tracksSession
    @property
    def tracksSession(self):
        return self.owner.getTracksSession()

#___________________________________________________________________________________________________ GS: analysisSession
    @property
    def analysisSession(self):
        return self.owner.getAnalysisSession()

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ initializeFolder
    def initializeFolder(self, *args):
        """ Initializes a folder within the root analysis path by removing any existing contents
            and then creating a new folder if it does not already exist. """
        path = self.getPath(*args, isDir=True)
        if os.path.exists(path):
            SystemUtils.remove(path)
        os.makedirs(path)
        return path

#___________________________________________________________________________________________________ getPath
    def getPath(self, *args, **kwargs):
        """ Convenience method for creating paths relative to the output root path for this
            Analyzer. """
        return self.owner.getPath(*args, **kwargs)

#___________________________________________________________________________________________________ getTempFilePath
    def getTempFilePath(self, name =None, extension =None, *args):
        """ Used to create a temporary file path within this instance's temporary folder.
            Any file on this path will be automatically removed at the end of the analysis
            process.

            [name] :: String :: None
                The desired file name for the desired file within the temporary directory. If no
                name is specified, a name will be created automatically using the current time
                (microsecond) and a 16 digit random code for a very low probability of collisions.

            [extension] :: String :: None
                Specifies the extension to add to this file. The file name is not altered if no
                extension is specified.

            [*args] :: [String] :: []
                A list of relative folder prefixes in which the file should reside. For example,
                if you wish to have a file 'bar' in a folder 'foo' then you would specify 'foo' as
                the single arg to get a file located at 'foo/bar' within the temporary file. No
                directory prefixes will be created within this method. """

        return self.owner.getTempFilePath(name=name, extension=extension, *args)

#___________________________________________________________________________________________________ getTempPath
    def getTempPath(self, *args, **kwargs):
        """ Creates a path relative to this instance's root temporary path. Uses the
            FileUtils.createPath() format for args and kwargs. """
        return self.owner.getTempPath(*args, **kwargs)

#___________________________________________________________________________________________________ analyze
    def analyze(self):
        """ Executes the analysis process for this stage, which consists largely of calling the
            analysis hook methods in their specified order. """

        # resets the cache
        self.cache.unload()

        self._startTime = TimeUtils.getNowDatetime()
        self._writeHeader()
        self._preAnalyze()
        self._analyze()
        self._postAnalyze()
        self._writeFooter()

#___________________________________________________________________________________________________ mergePdfs
    def mergePdfs(self, paths, fileName =None):
        """ Takes a list of paths to existing PDF files and merges them into a single pdf with
            the given file name.

            [fileName] :: String :: None
                The name of the file to be written. If not specified, a file name will be created
                using the name of this class. """

        merger = PdfFileMerger()
        for p in paths:
            with open(p, 'rb') as f:
                merger.append(PdfFileReader(f))

        if not fileName:
            fileName = '%s-Report.pdf' % self.__class__.__name__
        if not StringUtils.toStr2(fileName).endswith('.pdf'):
            fileName += '.pdf'

        with open(self.getPath(fileName, isFile=True), 'wb') as f:
            merger.write(f)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _writeHeader
    def _writeHeader(self):
        """ Method for writing the logging header for this stage. This is the first method called
            during the analysis process to denote in the log file that the following output was
            created by this stage. """

        self.logger.write([
            '\n' + 80*'*',
            '[STARTED]: %s STAGE' % self._label.upper(),
            '  * Run on %s' % TimeUtils.toZuluFormat(self._startTime).replace('T', ' at ')
        ] + self._getHeaderArgs(), indent=False)

#___________________________________________________________________________________________________ _getHeaderArgs
    # noinspection PyMethodMayBeStatic
    def _getHeaderArgs(self):
        """ A hook method used to add information to the log header for this stage. """
        return []

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        """ A hook method called just before starting the analysis process. """
        pass

#___________________________________________________________________________________________________ _analyze
    def _analyze(self):
        """ The core method in the analysis process. Unless overridden directly or by callback,
            this method will iterate through the sitemaps in the database and call the
            _analyzeSitemap() method on each one. """

        for sitemap in self.owner.getSitemaps():
            if sitemap.isReady:
                self._analyzeSitemap(sitemap)

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        """ Iterates over each trackway within the specified sitemap and calls the
            _analyzeTrackway() method on each one.

            sitemap :: Tracks_SiteMap
                The sitemap model instance to analyze. """

        for tw in self.owner.getTrackways(sitemap):
            self._analyzeTrackway(tw, sitemap)

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        """ Iterates over each track series in the trackway and calls the _analyzeTrackSeries()
            method on each one.

            trackway :: Tracks_Trackway
                The trackway instance to analyze.

            sitemap :: Tracks_SiteMap
                The sitemap in which this trackway resides. """

        for series in self.owner.getSeriesBundle(trackway).asList():
            if series.isReady:
                self._analyzeTrackSeries(series, trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        """ Iterates over the tracks within the track series and calls the _analyzeTrack() method
            on each one.

            series :: TrackSeries
                The TrackSeries instance to analyze.

            trackway :: Tracks_Trackway
                The trackway instance in which the track series resides.

            sitemap :: Tracks_Sitemap
                The sitemap in which the track series resides. """

        for t in series.tracks:
            self._analyzeTrack(t, series, trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """ Analyzes the specified track. By default nothing happens unless a trackCallback has
            been specified. This method should be otherwise overridden to analyze each track
            according to the analysis requirements.

            track :: Tracks_Track
                The track to analyze

            series :: TrackSeries
                The TrackSeries instance in which the track resides.

            trackway :: Tracks_Trackway
                The trackway instance in which the track resides.

            sitemap :: Tracks_Sitemap
                The sitemap in which the track resides. """
        pass

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """ A hook method called when the analysis process completes. """
        pass

#___________________________________________________________________________________________________ _writeFooter
    def _writeFooter(self):
        """ The final method called in the analysis process, which writes the final information
            about the analysis stage to the log file for reference. This includes basic operational
            information about performance by default. """

        elapsed = TimeUtils.getElapsedTime(
            startDateTime=self._startTime,
            endDateTime=TimeUtils.getNowDatetime(),
            toUnit=TimeUtils.MILLISECONDS)

        self.logger.write([
            '\n' + 80*'_',
            '[COMPLETE]: %s ANALYSIS STAGE' % self._label.upper(),
            '  * Elapsed Time: %s' % TimeUtils.toPrettyElapsedTime(elapsed)
        ] + self._getFooterArgs(), indent=False)

#___________________________________________________________________________________________________ _getFooterArgs
    # noinspection PyMethodMayBeStatic
    def _getFooterArgs(self):
        """ Specifies additional arguments to be written to the log file as part of the analysis
            footer. This method returns an empty list by default. """
        return []

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

