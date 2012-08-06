# CadenceData.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import os
import json

from cadence.config.ConfigReader import ConfigReader
from cadence.shared.io.channels.DataChannel import DataChannel
from cadence.util.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ CadenceData
class CadenceData(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _CONFIGS_KEY    = 'configs'
    _NAME_KEY       = 'name'
    _CHANNELS_KEY   = 'channels'
    _DATA_PATH      = os.path.abspath(os.path.dirname(__file__)).split('src')[0] + 'data' + os.sep

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """ Creates a new instance of CadenceData.

            @@@param name:string
                The name identifying the data.
        """

        self._name     = ArgsUtils.get('name', None, kwargs)
        self._configs  = ArgsUtils.get('configs', dict(), kwargs)
        self._channels = ArgsUtils.get('tracks', dict(), kwargs)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        """The name identifier for the CadenceData instance."""
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

#___________________________________________________________________________________________________ GS: configs
    @property
    def configs(self):
        """The Cadence configs object associated with the data."""
        return self._configs
    @configs.setter
    def configs(self, value):
        self._configs = value

#___________________________________________________________________________________________________ GS: channels
    @property
    def channels(self):
        """Data keyframe channels in the created/loaded dataset."""
        return self._channels

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ addChannel
    def addChannel(self, name, channelData):
        if isinstance(channelData, DataChannel):
            self._channels[name] = channelData
        else:
            self._channels[name] = DataChannel(name=name, **channelData)

#___________________________________________________________________________________________________ loadFile
    def loadFile(self, path):
        """ Same as the load method, except the data is loaded from the file specified by path,
            relative to Cadence's root data folder.

            @@@param path:string
                Relative path to the Cadence data file to open.

            @@@return bool
                True if the load was successful, False otherwise.
        """

        try:
            f    = open(path, 'r')
            data = f.read()
            f.close()
        except Exception, err:
            print 'FAILED: Unable to load Cadence data from file ' + path, err
            return False

        return self.load(data)

#___________________________________________________________________________________________________ load
    def load(self, data):
        """ Loads the data into the CadenceData instance, parsing if necessary beforehand.

            @@@param load:string,dict
                Either a string or dictionary representation of valid Cadence Interchange Data
                formatted data to be loaded.

            @@@return bool
                True if successful, False if the load process failed because of invalid data.
        """

        if isinstance(data, basestring):
            try:
                data = json.loads(data)
            except Exception, err:
                print 'FAILED: Loading Cadence data from JSON string.', err
                return False

        if CadenceData._NAME_KEY in data:
            self._name = data.get(CadenceData._NAME_KEY)

        if CadenceData._CONFIGS_KEY in data:
            self._configs = ConfigReader.fromDict(data.get(CadenceData._CONFIGS_KEY))

        if CadenceData._CHANNELS_KEY in data:
            channels = []
            for c in data.get(CadenceData._CHANNELS_KEY, []):
                channels.append(DataChannel.fromDict(c))

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

        data = dict()
        if self._configs:
            data[CadenceData._CONFIGS_KEY] = self._configs.toDict()

        if self._name:
            data['name'] = self._name

        if self._channels:
            channels = dict()
            for n,v in self._channels.iteritems():
                channels[n] = v.toDict()
            data['channels'] = channels

        try:
            data = json.dumps(data)
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

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________