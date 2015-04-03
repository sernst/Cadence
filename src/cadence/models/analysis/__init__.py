# __init__.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.sqlalchemy.PyGlassModelUtils import PyGlassModelUtils

DATABASE_URL = 'Cadence://analysis'
MODELS = PyGlassModelUtils.modelsInit(DATABASE_URL, __path__, __name__)
