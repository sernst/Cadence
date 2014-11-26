# CsvWriter.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import OrderedDict
import csv

from pyaid.string.StringUtils import StringUtils

#*************************************************************************************************** CsvWriter
class CsvWriter(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of CsvWriter."""
        self._fields    = OrderedDict()
        self.path       = kwargs.get('path')
        self.rows       = kwargs.get('rows', [])

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: fieldNames
    @property
    def fieldNames(self):
        out = []
        for k, n in self._fields.items():
            out.append(n)
        return out

#___________________________________________________________________________________________________ GS: fieldKeys
    @property
    def fieldKeys(self):
        out = []
        for k, n in self._fields.items():
            out.append(k)
        return out

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ addFields
    def addFields(self, *args):
        """ Tuples containing key, name pairs"""
        for arg in args:
            if StringUtils.isStringType(arg):
                self.addField(arg, arg)
            else:
                self.addField(arg[0], arg[1])

#___________________________________________________________________________________________________ addField
    def addField(self, key, name):
        """addField doc..."""
        self._fields[key] = name

#___________________________________________________________________________________________________ addRow
    def addRow(self, rowData):
        """addRow doc..."""
        self.rows.append(rowData)

#___________________________________________________________________________________________________ createRow
    def createRow(self, **kwargs):
        """addRow doc..."""
        self.addRow(kwargs)

#___________________________________________________________________________________________________ save
    def save(self):
        """save doc..."""
        try:
            with open(self.path, 'wb') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldNames, dialect=csv.excel)
                writer.writeheader()
                for row in self.rows:
                    result = dict()
                    for k, v in row.items():
                        result[self._fields[k]] = v
                    writer.writerow(result)
            return True
        except Exception:
            return False

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

