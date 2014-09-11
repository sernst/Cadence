# FlagsTracksDefault.py
# (C)2014
# Scott Ernst

import sqlalchemy as sqla

from pyglass.sqlalchemy.PyGlassModelsDefault import PyGlassModelsDefault
from pyglass.sqlalchemy.ConcretePyGlassModelsMeta import ConcretePyGlassModelsMeta

#___________________________________________________________________________________________________ FlagsTracksDefault
class FlagsTracksDefault(PyGlassModelsDefault):

#===================================================================================================
#                                                                                       C L A S S

    __metaclass__ = ConcretePyGlassModelsMeta
    __abstract__  = True

    _flags               = sqla.Column(sqla.Integer,     default=0)
    _sourceFlags         = sqla.Column(sqla.Integer,     default=0)
    _displayFlags        = sqla.Column(sqla.Integer,     default=0)
    _importFlags         = sqla.Column(sqla.Integer,     default=0)
    _analysisFlags       = sqla.Column(sqla.Integer,     default=0)
