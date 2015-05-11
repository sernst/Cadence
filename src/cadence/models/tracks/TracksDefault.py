# TracksDefault.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla

from pyglass.sqlalchemy.PyGlassModelsDefault import PyGlassModelsDefault
from pyglass.sqlalchemy.ConcretePyGlassModelsMeta import ConcretePyGlassModelsMeta
import six

#___________________________________________________________________________________________________ TracksDefault
@six.add_metaclass(ConcretePyGlassModelsMeta)
class TracksDefault(PyGlassModelsDefault):

#===================================================================================================
#                                                                                       C L A S S

    __abstract__  = True

    _ANALYSIS_PAIR_KEY = 'analysisPair'

    _flags               = sqla.Column(sqla.Integer,     default=0)
    _sourceFlags         = sqla.Column(sqla.Integer,     default=0)
    _displayFlags        = sqla.Column(sqla.Integer,     default=0)
    _importFlags         = sqla.Column(sqla.Integer,     default=0)
    _analysisFlags       = sqla.Column(sqla.Integer,     default=0)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: analysisPair
    @property
    def analysisPair(self):
        return self.fetchTransient(self._ANALYSIS_PAIR_KEY)


#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getAnalysisPair
    def getAnalysisPair(self, analysisSession, createIfMissing =True):
        """getAnalysisPair doc..."""

        target = self.fetchTransient(self._ANALYSIS_PAIR_KEY)
        if target and (analysisSession is None or analysisSession == target.mySession):
            return target

        if analysisSession is None:
            raise ValueError, 'Must provide a valid analysis session to retrieve an analysis pair'

        result = self._getAnalysisPair(analysisSession, createIfMissing=createIfMissing)
        self.putTransient(self._ANALYSIS_PAIR_KEY, result)
        return result

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getAnalysisPair
    def _getAnalysisPair(self, session, createIfMissing):
        """_getAnalysisPair doc..."""
        return None
