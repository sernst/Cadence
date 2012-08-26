# GaitVisualizer.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from cadence.config.enum.GaitConfigEnum import GaitConfigEnum
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum
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

        self._data = CadenceData()

        self._filename = ArgsUtils.get('filename', None, kwargs)
        if self._filename:
            self._data.loadFile(self._filename)
        else:
            self._data.load(ArgsUtils.get('data', None, kwargs))

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

        groupItems = []

        for c in self._data.getChannelsByKind(ChannelsEnum.POSITION):
            isHind = c.target in [TargetsEnum.LEFT_HIND, TargetsEnum.RIGHT_HIND]
            radius = 20 if isHind else 15
            res    = cmds.polySphere(radius=radius, name=c.target)
            groupItems.append(res[0])
            for k in c.keys:
                frames = [
                    ['translateX', k.value.x, k.inTangentMaya[0], k.outTangentMaya[0]],
                    ['translateY', k.value.y, k.inTangentMaya[1], k.outTangentMaya[1]],
                    ['translateZ', k.value.z, k.inTangentMaya[2], k.outTangentMaya[2]]
                ]
                for f in frames:
                    cmds.setKeyframe(
                        res[0],
                        attribute=f[0],
                        time=k.time,
                        value=f[1],
                        inTangentType=f[2],
                        outTangentType=f[3]
                    )

                if k.event == 'land':
                    printResult = cmds.polyCylinder(
                        name=c.target + '_print1',
                        radius=radius,
                        height=(1.0 if isHind else 5.0)
                    )
                    cmds.move(k.value.x, k.value.y, k.value.z, printResult[0])
                    groupItems.append(printResult[0])

        name = 'cycle_phase' + str(self._data.configs.get(GaitConfigEnum.PHASE)) + \
               '_hind' + str(self._data.configs.get(GaitConfigEnum.DUTY_FACTOR_HIND)) + \
               '_fore' + str(self._data.configs.get(GaitConfigEnum.DUTY_FACTOR_FORE))

        cmds.group(*groupItems, world=True, name=name)

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
