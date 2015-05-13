# Analysis_Track.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla

from cadence.models.analysis.AnalysisDefault import AnalysisDefault

#___________________________________________________________________________________________________ Analysis_Track
class Analysis_Track(AnalysisDefault):
    """ Doc... """

#===================================================================================================
#                                                                                       C L A S S

    __tablename__ = 'tracks'

    _uid                = sqla.Column(sqla.Unicode, default='')
    _curveSegment       = sqla.Column(sqla.Integer, default=-2)
    _curveIndex         = sqla.Column(sqla.Integer, default=-1)
    _segmentPosition    = sqla.Column(sqla.Float, default=0.0)
    _curvePosition      = sqla.Column(sqla.Float, default=0.0)
    _nextCurveTrack     = sqla.Column(sqla.Unicode, default='')


