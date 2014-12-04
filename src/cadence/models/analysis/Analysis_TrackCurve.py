# Analysis_TrackCurve.py
# (C)2014
# Scott Ernst and Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division

from array import array

from pyaid.string.ByteChunk import ByteChunk

import sqlalchemy as sqla
from cadence.analysis.shared.PositionValue2D import PositionValue2D

from cadence.models.analysis.AnalysisDefault import AnalysisDefault


#___________________________________________________________________________________________________ Analysis_TrackCurve
class Analysis_TrackCurve(AnalysisDefault):
    """ Doc... """

#===================================================================================================
#                                                                                       C L A S S

    __tablename__ = 'track_curves'

    _seriesName = sqla.Column(sqla.Unicode, default='')
    _pointBlob  = sqla.Column(sqla.LargeBinary)

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        super(Analysis_TrackCurve, self).__init__(**kwargs)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: points
    @property
    def points(self):
        """ Returns a list of position value objects (x, z, xUnc, zUnc) corresponding to the points
            in the curve """
        out = self.fetchTransient('points')
        if out is None:
            bc  = ByteChunk(sourceBytes=self.pointBlob)
            a   = bc.readArrayChunk('d')
            out = []
            i   = 0

            while i < len(a):
                out.append(PositionValue2D(a[i], a[i+1], a[i+2], a[i+3]))
                i += 4

            out = tuple(out)
            self.putTransient('points', out)
        return out
    @points.setter
    def points(self, value):
        if not value:
            self.putTransient('points', [])
            self.points = None
            return

        self.putTransient('points', value)
        store = array('d')
        for point in value:
            store.extend(point.toTuple())
        bc = ByteChunk()
        bc.writeArrayChunk(store)
        self.points = bc.byteArray

