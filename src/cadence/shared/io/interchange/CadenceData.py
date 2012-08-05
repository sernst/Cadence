# CadenceData.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import os
import json
import itertools

from cadence.util.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ CadenceData
class CadenceData(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _DATA_PATH = os.path.abspath(os.sep.join([
        x for x in itertools.takewhile(lambda x: x != 'src',
        os.path.dirname(__file__).strip(os.sep).split(os.sep))
    ].append('data')))

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """ Creates a new instance of CadenceData.

            @@@param name:string
                The name identifying the data.
        """

        self._name    = ArgsUtils.get('name', None, kwargs)
        self._configs = ArgsUtils.get('configs', None, kwargs)
        self._data    = ArgsUtils.get('data', None, kwargs)
        if isinstance(self._data, basestring):
            self.load(self._data)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: configs
    @property
    def configs(self):
        return self._configs
    @configs.setter
    def configs(self, value):
        self._configs = value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ loadFile
    def loadFile(self, path):
        """Doc..."""

        f    = open(path, 'r')
        data = f.read()
        f.close()

        return self.load(data)

#___________________________________________________________________________________________________ load
    def load(self, data):
        """Doc..."""

        if isinstance(data, basestring):
            try:
                data = json.loads(data)
            except Exception, err:
                print 'FAILED: Loading Cadence data from JSON string.', err
                return False

        self._data = data
        return True

#___________________________________________________________________________________________________ write
    def write(self, folder =None, name =None):
        """ Writes the Cadence data to an encoded string and returns that string. If a path is
            specified, it will also write the data to that file before returning the string. If the
            writing process fails, None is returned instead.

            @@@param folder:string
                The folder where the file should be written relative to Cadence's root data
                directory.

            @@@param name:string
                If specified this value will override the CadenceData instance's name for the
                file to be written.
        """

        try:
            data = json.dumps(self._data)
        except Exception, err:
            print 'FAILED: Writing Cadence data.', err
            return None

        if folder:
            name = name if name else (self._name if self._name else 'data')
            if not name.endswith('.cadence'):
                name += '.cadence'
            path = os.path.join(CadenceData._DATA_PATH, folder, name)
            try:
                f = open(path, 'w')
                f.write(data)
                f.close()
            except Exception, err:
                print 'FAILED: Writing Cadence file.', err

        return data

