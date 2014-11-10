# FlagsTracksDefault.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla

from pyglass.sqlalchemy.PyGlassModelsDefault import PyGlassModelsDefault
from pyglass.sqlalchemy.ConcretePyGlassModelsMeta import ConcretePyGlassModelsMeta
import six

#___________________________________________________________________________________________________ FlagsTracksDefault
@six.add_metaclass(ConcretePyGlassModelsMeta)
class FlagsTracksDefault(PyGlassModelsDefault):

#===================================================================================================
#                                                                                       C L A S S

    __abstract__  = True

    _flags               = sqla.Column(sqla.Integer,     default=0)
    _sourceFlags         = sqla.Column(sqla.Integer,     default=0)
    _displayFlags        = sqla.Column(sqla.Integer,     default=0)
    _importFlags         = sqla.Column(sqla.Integer,     default=0)
    _analysisFlags       = sqla.Column(sqla.Integer,     default=0)
