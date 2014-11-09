# DataIntegrityTester.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.string.StringUtils import StringUtils

from cadence.enum.SourceFlagsEnum import SourceFlagsEnum
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ DataIntegrityTester
class DataIntegrityTester(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of DataIntegrityTester."""
        pass

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: propertyName
    @property
    def propertyName(self):
        return None
    @propertyName.setter
    def propertyName(self, value):
        pass

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ run
    def run(self):
        """Doc..."""
        self._getTracks()
        return True

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getTracks
    def _getTracks(self):
        """Doc..."""

        model   = Tracks_Track.MASTER
        session = model.createSession()
        column  = getattr(model, TrackPropEnum.SOURCE_FLAGS.name)
        result  = session.query(model).filter(column.op('&')(SourceFlagsEnum.COMPLETED) == 1).all()

        print('Result:', len(result))


#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return StringUtils.toUnicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
