# Analysis_Track.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.number.NumericUtils import NumericUtils

import sqlalchemy as sqla

from cadence.models.analysis.AnalysisDefault import AnalysisDefault

#_______________________________________________________________________________
class Analysis_Track(AnalysisDefault):
    """ Doc... """

#===============================================================================
#                                                                                       C L A S S

    __tablename__ = 'tracks'

    _uid                = sqla.Column(sqla.Unicode, default='')

    #--- Status Analyzer ---#
    _trackwayIndex      = sqla.Column(sqla.Integer, default=0)
    _trackwayName       = sqla.Column(sqla.Unicode, default='')

    #--- Curvature Analyzer ---#
    _curveSegment       = sqla.Column(sqla.Integer, default=-2)
    _curveIndex         = sqla.Column(sqla.Integer, default=-1)
    _segmentPosition    = sqla.Column(sqla.Float, default=0.0)
    _curvePosition      = sqla.Column(sqla.Float, default=0.0)
    _nextCurveTrack     = sqla.Column(sqla.Unicode, default='')

    #--- Validation Analyzer ---#
    _strideLength       = sqla.Column(sqla.Float, default=0.0)
    _strideLengthUnc    = sqla.Column(sqla.Float, default=0.0)

    _paceLength         = sqla.Column(sqla.Float, default=0.0)
    _paceLengthUnc      = sqla.Column(sqla.Float, default=0.0)

    #--- Direction Analyzer ---#
    _headingAngle         = sqla.Column(sqla.Float, default=0.0)
    _headingAngleUnc      = sqla.Column(sqla.Float, default=0.0)

    #--- Gauge Analyzer ---#
    _simpleGauge        = sqla.Column(sqla.Float, default=0.0)
    _simpleGaugeUnc     = sqla.Column(sqla.Float, default=0.0)

#===============================================================================
#                                                                                   G E T / S E T

    #___________________________________________________________________________
    @property
    def paceLengthValue(self):
        return NumericUtils.toValueUncertainty(
            self.paceLength, self.paceLengthUnc)

    #___________________________________________________________________________
    @property
    def strideLengthValue(self):
        return NumericUtils.toValueUncertainty(
            self.strideLength, self.strideLengthUnc)

    #___________________________________________________________________________
    @property
    def gaugeValue(self):
        return NumericUtils.toValueUncertainty(
            self.simpleGauge, self.simpleGaugeUnc)
