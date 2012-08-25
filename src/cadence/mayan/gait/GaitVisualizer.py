# GaitVisualizer.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.io.CadenceData import CadenceData
from cadence.util.ArgsUtils import ArgsUtils
from nimble import cmds

#___________________________________________________________________________________________________ GaitVisualizer
class GaitVisualizer(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, *args, **kwargs):
        """Creates a new instance of GaitVisualizer."""
        self._filename = ArgsUtils.get('filename', None, kwargs, args, 0)
        if not self._filename:
            return

        self._data = CadenceData()
        self._data.loadFile(self._filename)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: filename
    @property
    def filename(self):
        return self._filename

#___________________________________________________________________________________________________ GS: data
    @property
    def data(self):
        return self._data

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ buildScene
    def buildScene(self):
        """Doc..."""

        for c in self._data.getChannelsByKind(ChannelsEnum.POSITION):
            res = cmds.polySphere(radius=20, name=c.name)
            for k in c.keys:
                frames = [
                    ['translateX', k.value.x],
                    ['translateY', k.value.y],
                    ['translateZ', k.value.z]
                ]
                for f in frames:
                    cmds.setKeyframe(
                        res[0],
                        attribute=f[0],
                        time=k.time,
                        value=f[1],
                        inTangentType=k.inTangentMaya,
                        outTangentType=k.outTangentMaya
                    )

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return unicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
