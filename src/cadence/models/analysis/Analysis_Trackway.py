# Analysis_Trackway.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla

from cadence.models.analysis.AnalysisDefault import AnalysisDefault

#___________________________________________________________________________________________________ Analysis_Trackway
class Analysis_Trackway(AnalysisDefault):
    """ Doc... """

#===================================================================================================
#                                                                                       C L A S S

    __tablename__ = 'trackways'

    _index = sqla.Column(sqla.Integer,     default=0)

    #-- Curvature Analyzer ---#
    _curveSeries  = sqla.Column(sqla.Unicode, default='')
    _curveLength  = sqla.Column(sqla.Float, default=0.0)

    #--- Gauge Analyzer ---#
    _simpleGauge        = sqla.Column(sqla.Float, default=0.0)
    _simpleGaugeUnc     = sqla.Column(sqla.Float, default=0.0)
