# __init__.py
# (C)2014
# Scott Ernst

from pyglass.sqlalchemy.PyGlassModelUtils import PyGlassModelUtils

DATABASE_URL = 'Cadence://analysis'
MODELS = PyGlassModelUtils.modelsInit(DATABASE_URL, __path__, __name__)
