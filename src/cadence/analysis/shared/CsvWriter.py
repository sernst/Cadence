# CsvWriter.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import OrderedDict
import csv

from pyaid.string.StringUtils import StringUtils
from pyaid.system.SystemUtils import SystemUtils

#*************************************************************************************************** CsvWriter
class CsvWriter(object):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of CsvWriter."""
        self.path               = kwargs.get('path')
        self.rows               = kwargs.get('rows', [])
        self.autoIndexFieldName = kwargs.get('autoIndexFieldName', None)
        self.removeIfSavedEmpty = kwargs.get('removeIfSavedEmpty', True)
        self._fields            = OrderedDict()

        if 'fields' in kwargs:
            self.addFields(*kwargs.get('fields'))

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def fieldNames(self):
        out = []
        for k, n in self._fields.items():
            out.append(n)
        return out

#_______________________________________________________________________________
    @property
    def fieldKeys(self):
        out = []
        for k, n in self._fields.items():
            out.append(k)
        return out

#_______________________________________________________________________________
    @property
    def count(self):
        return len(self.rows)

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def addFields(self, *args):
        """ Tuples containing key, name pairs"""
        for arg in args:
            if StringUtils.isStringType(arg):
                self.addField(arg, arg)
            else:
                self.addField(arg[0], arg[1])

#_______________________________________________________________________________
    def addField(self, key, name):
        """addField doc..."""
        self._fields[key] = name

#_______________________________________________________________________________
    def addRow(self, rowData):
        """addRow doc..."""
        self.rows.append(rowData)

#_______________________________________________________________________________
    def createRow(self, **kwargs):
        """addRow doc..."""
        self.addRow(kwargs)

#_______________________________________________________________________________
    def save(self):
        """save doc..."""
        if self.removeIfSavedEmpty and not self.rows:
            self.remove()
            return

        index = 0
        names = self.fieldNames
        if self.autoIndexFieldName:
            names.insert(0, self.autoIndexFieldName)

        try:
            with open(self.path, 'wb') as f:
                writer = csv.DictWriter(f, fieldnames=names, dialect=csv.excel)
                writer.writeheader()
                for row in self.rows:
                    result = dict()

                    if self.autoIndexFieldName:
                        index += 1
                        result[self.autoIndexFieldName] = index

                    for key, name in self._fields.items():
                        value = row.get(key, '')
                        if StringUtils.isTextType(value):
                            value = value.encode('latin-1')
                        result[name] = value
                    writer.writerow(result)
            return True
        except Exception:
            return False

#_______________________________________________________________________________
    def remove(self):
        """remove doc..."""
        return SystemUtils.remove(self.path)

#===============================================================================
#                                                                               I N T R I N S I C

#_______________________________________________________________________________
    def __repr__(self):
        return self.__str__()

#_______________________________________________________________________________
    def __str__(self):
        return '<%s>' % self.__class__.__name__

