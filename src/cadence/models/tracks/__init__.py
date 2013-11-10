# __init__.py
# (C)2013
# Scott Ernst

from pyglass.sqlalchemy.PyGlassModelUtils import PyGlassModelUtils

DATABASE_URL = 'Cadence://tracks'
MODELS = PyGlassModelUtils.modelsInit(__path__, __name__)
