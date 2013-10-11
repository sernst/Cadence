# TracksDefault.py
# (C)2013
# Scott Ernst

from sqlalchemy import Column
from sqlalchemy import Unicode

from pyglass.sqlalchemy.PyGlassModelsDefault import PyGlassModelsDefault
from pyglass.sqlalchemy.ConcretePyGlassModelsMeta import ConcretePyGlassModelsMeta

#___________________________________________________________________________________________________ TracksDefault
class TracksDefault(PyGlassModelsDefault):

#===================================================================================================
#                                                                                       C L A S S

    __metaclass__ = ConcretePyGlassModelsMeta
    __abstract__  = True

    # The base 64 identifier for the item
    _id = Column(Unicode, default=u'')

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        return self._createDict()

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _createDict
    def _createDict(self, **kwargs):
        kwargs['id'] = self.id
        return kwargs
