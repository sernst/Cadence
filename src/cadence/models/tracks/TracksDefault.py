# TracksDefault.py
# (C)2013
# Scott Ernst

from pyaid.radix.Base64 import Base64

from pyglass.sqlalchemy.PyGlassModelsDefault import PyGlassModelsDefault
from pyglass.sqlalchemy.ConcretePyGlassModelsMeta import ConcretePyGlassModelsMeta

#___________________________________________________________________________________________________ TracksDefault
class TracksDefault(PyGlassModelsDefault):

#===================================================================================================
#                                                                                       C L A S S

    __metaclass__ = ConcretePyGlassModelsMeta
    __abstract__  = True

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: propertyName
    @property
    def id(self):
        return Base64.to64(self.i)

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
