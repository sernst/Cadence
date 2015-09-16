# CsvWriter.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import OrderedDict
import csv
from pyaid.dict.DictUtils import DictUtils
from pyaid.file.FileUtils import FileUtils

from pyaid.string.StringUtils import StringUtils
from pyaid.system.SystemUtils import SystemUtils

#*******************************************************************************
class CsvWriter(object):
    """A class for..."""

    #___________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of CsvWriter."""
        self.rows               = kwargs.get('rows', [])
        self.autoIndexFieldName = kwargs.get('autoIndexFieldName', None)
        self.removeIfSavedEmpty = kwargs.get('removeIfSavedEmpty', True)
        self._path              = kwargs.get('path')
        self._fields            = OrderedDict()

        if 'fields' in kwargs:
            self.addFields(*kwargs.get('fields'))

    #===========================================================================
    #                                                             G E T / S E T

    #___________________________________________________________________________
    @property
    def path(self):
        if not self._path:
            return None
        if not StringUtils.ends(self._path, '.csv'):
            if not FileUtils.getFileExtension(self._path):
                self._path += '.csv'
        return FileUtils.cleanupPath(self._path, isFile=True)
    @path.setter
    def path(self, value):
        self._path = value

    #___________________________________________________________________________
    @property
    def fieldNames(self):
        out = []
        for key, spec in self._fields.items():
            out.append(spec.get('name', key))
        return out

    #___________________________________________________________________________
    @property
    def fieldKeys(self):
        out = []
        for key, spec in self._fields.items():
            out.append(key)
        return out

    #___________________________________________________________________________
    @property
    def count(self):
        return len(self.rows)

    #===========================================================================
    #                                                               P U B L I C

    #___________________________________________________________________________
    def addFields(self, *args, **kwargs):
        """ Adds multiple fields at once. Arguments can be any mix of the
            following formats

            addFields(
                "keyAndValue", # String argument
                ("key", "value") # Tuple or list argument
                key="value" # Keyword argument
                key=("value")
            """
        for arg in args:
            if StringUtils.isStringType(arg):
                self.addField(arg)
            else:
                self.addField(*arg)

        for key, value in DictUtils.iter(kwargs):
            if StringUtils.isStringType(value):
                self.addField(key, value)
            else:
                self.addField(key, *value)

    #___________________________________________________________________________
    def addField(self, key, name =None, empty =None):
        """addField doc..."""
        self._fields[key] = dict(
            name=name if name else key,
            empty=empty if empty else None)

    #___________________________________________________________________________
    def addRow(self, rowData):
        """addRow doc..."""
        self.rows.append(rowData)

    #___________________________________________________________________________
    def createRow(self, **kwargs):
        """addRow doc..."""
        self.addRow(kwargs)

    #___________________________________________________________________________
    def save(self, path =None):
        """ Saves the CSV file data to the specified path """
        if path is None:
            path = self.path

        if self.removeIfSavedEmpty and not self.rows:
            self.remove()
            return

        index = 0
        names = self.fieldNames
        if self.autoIndexFieldName:
            names.insert(0, self.autoIndexFieldName)

        try:
            with open(path, 'wb') as f:
                writer = csv.DictWriter(f, fieldnames=names, dialect=csv.excel)
                writer.writeheader()
                for row in self.rows:
                    result = dict()

                    if self.autoIndexFieldName:
                        index += 1
                        result[self.autoIndexFieldName] = index

                    for key, spec in DictUtils.iter(self._fields):
                        value = row.get(key, spec.get('empty', ''))
                        name = spec.get('name', key)
                        if StringUtils.isTextType(value):
                            value = value.encode('latin-1')
                        result[name] = value
                    writer.writerow(result)
            return True
        except Exception:
            return False

    #___________________________________________________________________________
    def remove(self):
        """remove doc..."""
        return SystemUtils.remove(self.path)

    #===========================================================================
    #                                                         I N T R I N S I C

    #___________________________________________________________________________
    def __repr__(self):
        return self.__str__()

    #___________________________________________________________________________
    def __str__(self):
        return '<%s>' % self.__class__.__name__

