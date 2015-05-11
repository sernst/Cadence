# AnalysisDefault.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import namedtuple

from pyaid.config.ConfigsDict import ConfigsDict
from pyaid.radix.Base36 import Base36

import sqlalchemy as sqla

from pyglass.sqlalchemy.PyGlassModelsDefault import PyGlassModelsDefault
from pyglass.sqlalchemy.ConcretePyGlassModelsMeta import ConcretePyGlassModelsMeta
import six

#___________________________________________________________________________________________________ AnalysisDefault
@six.add_metaclass(ConcretePyGlassModelsMeta)
class AnalysisDefault(PyGlassModelsDefault):

#===================================================================================================
#                                                                                       C L A S S

    __abstract__  = True

    _flags               = sqla.Column(sqla.Integer,     default=0)
    _displayFlags        = sqla.Column(sqla.Integer,     default=0)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: id
    @property
    def id(self):
        return Base36.to36(self.i)

#___________________________________________________________________________________________________ GS: uid
    @property
    def uid(self):
        return '%s-%s' % (self.__class__.__name__, self.id)

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        """ Caching object used during analysis to store transient data related to this sitemap """
        out = self.fetchTransient('cache')
        if not out:
            out = ConfigsDict()
            self.putTransient('cache', out)
        return out
