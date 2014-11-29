# __init__.py
# (C)2013
# Scott Ernst

from pyglass.sqlalchemy.PyGlassModelUtils import PyGlassModelUtils

DATABASE_URL = 'Cadence://tracks'
MODELS = PyGlassModelUtils.modelsInit(DATABASE_URL, __path__, __name__)
