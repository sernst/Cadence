# TrackCsvImporter.py
# (C)2013
# Scott Ernst

import csv

from cadence.mayan.trackway.Track import Track

#___________________________________________________________________________________________________ TrackCsvImporter
class TrackCsvImporter(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, path =None):
        """Creates a new instance of TrackCsvImporter."""
        self._path   = path
        self._tracks = []

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ read
    def read(self, path =None, force =True):
        """Doc..."""
        if path is not None:
            self._path = path
        if self._path is None:
            return False

        with open(self._path, 'rU') as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            for row in reader:
                # Skip any rows that don't start with the proper numeric index value, which
                # includes the header row (if it exists) with the column names
                try:
                    index = int(row[0])
                except Exception, err:
                    continue

                t = Track.fromSpreadsheetEntry(row, force=force)
                self._tracks.append(t)

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return unicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
