# CadenceData.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import os
import json

from pyaid.ArgsUtils import ArgsUtils

from cadence.config.ConfigReader import ConfigReader
from cadence.shared.io.channel.DataChannel import DataChannel

#___________________________________________________________________________________________________ CadenceData
class CadenceData(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    VERSION         = 1
    EXTENSION       = '.cadence'

    ROOT_DATA_PATH  = os.path.abspath(os.path.dirname(__file__)).split('src')[0] + 'data' + os.sep

    _CONFIGS_KEY    = 'configs'
    _NAME_KEY       = 'name'
    _CHANNELS_KEY   = 'channels'

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """ Creates a new instance of CadenceData.

            @@@param name:string
                The name identifying the data.
        """

        self._name     = ArgsUtils.get('name', None, kwargs)
        self._configs  = ArgsUtils.get('configs', None, kwargs)
        self._channels = ArgsUtils.get('channels', [], kwargs)

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

#___________________________________________________________________________________________________ toString
    def echo(self):
        print self.toString()

#___________________________________________________________________________________________________ toString
    def toString(self):
        out = []
        for ch in self.channels:
            out.append(ch.toString())
        return u'\n'.join(out)

#___________________________________________________________________________________________________ getChannelByName
    def getChannelByName(self, name):
        for c in self._channels:
            if c.name == name:
                return c

        return None

#___________________________________________________________________________________________________ getChannels
    def getChannels(self, kind =None, target =None):
        if not kind and not target:
            return self.channels

        if not kind:
            return self.getChannelsByTarget(target)

        if not target:
            return self.getChannelsByKind(kind)

        out = []
        for c in self._channels:
            if c.kind == kind and c.target == target:
                out.append(c)

        return out

#___________________________________________________________________________________________________ getChannelsByKind
    def getChannelsByKind(self, kind):
        out = []
        for c in self._channels:
            if c.kind == kind:
                out.append(c)

        return out if out else None

#___________________________________________________________________________________________________ getChannelsByTarget
    def getChannelsByTarget(self, target):
        out = []
        for c in self._channels:
            if c.target == target:
                out.append(c)

        return out if out else None

#___________________________________________________________________________________________________ createChannel
    def createChannel(self, name, channelData):
        self._channels.append(DataChannel(name=name, **channelData))

#___________________________________________________________________________________________________ addChannel
    def addChannel(self, channelData):
        self._channels.append(channelData)

#___________________________________________________________________________________________________ addChannels
    def addChannels(self, channels):
        if isinstance(channels, list):
            for v in channels:
                self.addChannel(v)
        elif isinstance(channels, dict):
            for n,v in channels.iteritems():
                self.addChannel(v)

#___________________________________________________________________________________________________ loadFile
    def loadFile(self, path):
        """ Same as the load method, except the data is loaded from the file specified by path,
            relative to Cadence's root data folder.

            @@@param path:string
                Relative path to the Cadence data file to open.

            @@@return bool
                True if the load was successful, False otherwise.
        """

        sourcePath = path
        if not sourcePath.endswith(CadenceData.EXTENSION):
            sourcePath += CadenceData.EXTENSION

        if not os.path.exists(sourcePath):
            sourcePath = os.path.join(CadenceData.ROOT_DATA_PATH, path)
            if not os.path.exists(sourcePath):
                print 'FAILED: Unable to load Cadence data from missing file ' + path
                return False

        try:
            f    = open(sourcePath, 'r')
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

        if not data:
            return False

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
            for c in data.get(CadenceData._CHANNELS_KEY, dict()):
                self._channels.append(DataChannel.fromDict(c))

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

        data = {'version':CadenceData.VERSION}
        if self._configs:
            data[CadenceData._CONFIGS_KEY] = self._configs.toDict()

        if self._name:
            data['name'] = self._name

        if self._channels:
            channels = []
            for c in self._channels:
                channels.append(c.toDict())
            data['channels'] = channels

        try:
            data = json.dumps(data)
        except Exception, err:
            print 'FAILED: Writing Cadence data.', err
            return None

        if folder:
            name = name if name else (self._name if self._name else 'data')
            if not name.endswith(CadenceData.EXTENSION):
                name += CadenceData.EXTENSION
            path = os.path.join(CadenceData.ROOT_DATA_PATH, folder, name)
            outDir = os.path.dirname(path)

            try:
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
            except Exception, err:
                print 'FAILED: Unable to create output directory: ' + str(outDir)
                return None

            try:
                f = open(path, 'w')
                f.write(data)
                f.close()
            except Exception, err:
                print 'FAILED: Writing Cadence file.', err

        return data
