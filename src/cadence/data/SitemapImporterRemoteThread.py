# SitemapImporterRemoteThread.py
# (C)2014
# Scott Ernst

import os
import csv

from pyaid.ArgsUtils import ArgsUtils
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.reflection.Reflection import Reflection
from pyaid.string.StringUtils import StringUtils

from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread
from cadence.enum.SitemapCsvColumnEnum import SitemapCsvColumnEnum

from cadence.models.tracks.Tracks_Sitemap import Tracks_Sitemap

#___________________________________________________________________________________________________ SitemapImporterRemoteThread
class SitemapImporterRemoteThread(RemoteExecutionThread):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, path, session =None, **kwargs):
        """Creates a new instance of TrackImporterRemoteThread."""
        RemoteExecutionThread.__init__(self, parent, **kwargs)
        self._path       = path
        self._session    = session
        self._verbose    = ArgsUtils.get('verbose', True, kwargs)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _runImpl
    def _runImpl(self):
        model   = Tracks_Sitemap.MASTER
        session = self._session if self._session else model.createSession()

        try:
            self._log.write(u'<h1>Beginning Sitemap Import...</h1>')
            if self._path is None or not os.path.exists(self._path):
                self._log.write(u'<h2>Invalid or missing path</h2>')
                return 1

            # Delete all existing rows
            rowCount = session.query(model).count()
            if rowCount > 0:
                session.query(model).delete()

            with open(self._path, 'rU') as f:
                try:
                    reader = csv.reader(f, delimiter=',', quotechar='"')
                except Exception, err:
                    self._writeError({
                        'message':u'ERROR: Unable to read CSV file "%s"' % self._path,
                        'error':err })
                    return

                if reader is None:
                    self._writeError({
                        'message':u'ERROR: Failed to create CSV reader for file "%s"' % self._path })
                    return

                for row in reader:
                    # Skip any rows that don't start with the proper numeric index value, which
                    # includes the header row (if it exists) with the column names
                    try:
                        index = int(row[0])
                    except Exception, err:
                        continue

                    rowDict = dict()
                    for column in Reflection.getReflectionList(SitemapCsvColumnEnum):
                        value = row[column.index]

                        if not isinstance(value, unicode):
                            value = StringUtils.strToUnicode(value)

                        if value != u'' or value is None:
                            rowDict[column.name] = value

                    self._fromSpreadsheetEntry(rowDict, session)

        except Exception, err:
            if not self._session:
                session.rollback()
                session.close()

            self._log.writeError(u'ERROR: Sitemap Importing Error', err)
            return 1

        if self._session is None:
            session.commit()
            session.close()

        self._log.write(u'<h1>Sitemap Import Complete</h1>')
        return 0

#___________________________________________________________________________________________________ _fromSpreadsheetEntry
    def _fromSpreadsheetEntry(self, data, session):
        model = Tracks_Sitemap.MASTER
        sitemap = model()

        sitemap.index        = int(data[SitemapCsvColumnEnum.INDEX.name])
        sitemap.filename     = data.get(SitemapCsvColumnEnum.FILENAME.name, u'')
        sitemap.federalNorth = float(data.get(SitemapCsvColumnEnum.FEDERAL_NORTH.name, 0))
        sitemap.federalEast  = float(data.get(SitemapCsvColumnEnum.FEDERAL_EAST.name, 0))
        sitemap.left         = float(data.get(SitemapCsvColumnEnum.LEFT.name, 0))
        sitemap.top          = float(data.get(SitemapCsvColumnEnum.TOP.name, 0))
        sitemap.width        = float(data.get(SitemapCsvColumnEnum.WIDTH.name, 0))
        sitemap.height       = float(data.get(SitemapCsvColumnEnum.HEIGHT.name, 0))
        sitemap.xFederal     = float(data.get(SitemapCsvColumnEnum.FEDERAL_X.name, 0))
        sitemap.yFederal     = float(data.get(SitemapCsvColumnEnum.FEDERAL_Y.name, 0))
        sitemap.xTranslate   = float(data.get(SitemapCsvColumnEnum.TRANSLATE_X.name, 0))
        sitemap.zTranslate   = float(data.get(SitemapCsvColumnEnum.TRANSLATE_Z.name, 0))
        sitemap.xRotate      = float(data.get(SitemapCsvColumnEnum.ROTATE_X.name, 0))
        sitemap.yRotate      = float(data.get(SitemapCsvColumnEnum.ROTATE_Y.name, 0))
        sitemap.zRotate      = float(data.get(SitemapCsvColumnEnum.ROTATE_Z.name, 0))
        sitemap.scale        = float(data.get(SitemapCsvColumnEnum.SCALE.name, 0))

        session.add(sitemap)

        self._log.write(u'<div>CREATED: %s "%s"</div>' % (sitemap.index, sitemap.filename))
        return sitemap

#___________________________________________________________________________________________________ _writeError
    def _writeError(self, data):
        """ Writes import error data to the logger, formatting it for human readable display. """
        source = {}

        if 'data' in data:
            for n,v in data['data'].iteritems():
                source[u' '.join(n.split(u'_')).title()] = v

        indexPrefix = u''
        if 'index' in data:
            indexPrefix = u' [INDEX: %s]:' % data.get('index', u'Unknown')

        result  = [
            u'IMPORT ERROR%s: %s' % (indexPrefix, data['message']),
            u'DATA: ' + DictUtils.prettyPrint(source)]

        if 'existing' in data:
            source = {}
            for n,v in JSON.fromString(data['existing'].snapshot).iteritems():
                source[u' '.join(n.split(u'_')).title()] = v
            result.append(u'CONFLICT: ' + DictUtils.prettyPrint(source))

        if 'error' in data:
            self._logger.writeError(result, data['error'])
        else:
            self._logger.write(result)

