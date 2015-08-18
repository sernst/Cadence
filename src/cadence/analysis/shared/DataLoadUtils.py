# DataLoadUtils.py
# (C)2015
# Scott Ernst

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

import re

import pandas as pd
import sqlalchemy as sqla

from cadence.CadenceEnvironment import CadenceEnvironment

#_______________________________________________________________________________
def createEngine(analysis =False):
    """ Creates the SqlAlchemy engine to connect to the database and returns
        that engine.
    :return: Engine
    """
    name = 'analysis.vdb' if analysis else 'tracks.vdb'
    path = CadenceEnvironment.getLocalAppResourcePath(
        'data', name, isFile=True)
    url = 'sqlite:///%s' % path
    return sqla.create_engine(url)

#_______________________________________________________________________________
def readTable(tableName, analysis =False):
    """ Returns a Pandas DataFrame populated with the structure and data of the
        specified table in the database.
    :param tableName: str
    :return: DataFrame
    """
    frame =  pd.read_sql_table(tableName, createEngine(analysis=analysis))
    columns = list(frame.columns)
    for index in range(len(columns)):
        columns[index] = getSafeColumnName(columns[index])

    frame.columns = columns
    return frame

#_______________________________________________________________________________
def getSafeColumnName(name):
    """ Column names must begin with a letter character or underscore. If the
        name in question does not, it gets ab "X" prefixed to the name as is
        the convention in Pandas and other data science toolkits. Valid names
        are returned without editing.
    :param name: str
    :return: str
    """
    if re.compile('^[^a-zA-Z_]+').match(name):
        return 'X%s' % name
    return name
