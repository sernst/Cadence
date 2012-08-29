# TargetData.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import math

import numpy as np

from cadence.config.enum.SkeletonConfigEnum import SkeletonConfigEnum
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.TangentsEnum import TangentsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum
from cadence.util.ArgsUtils import ArgsUtils
from cadence.util.math3D.Vector3D import Vector3D
from cadence.shared.io.channel.DataChannel import DataChannel

#___________________________________________________________________________________________________ TargetData
class TargetData(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _FORE_TARGETS = [
        TargetsEnum.LEFT_FORE,
        TargetsEnum.RIGHT_FORE
    ]

    _LEFT_TARGETS = [
        TargetsEnum.LEFT_HIND,
        TargetsEnum.LEFT_FORE
    ]

#___________________________________________________________________________________________________ __init__
    def __init__(self, target, **kwargs):
        """Creates a new instance of TargetData."""
        self._target        = target
        self._channels      = ArgsUtils.get('channels', dict(), kwargs)
        self._dutyFactor    = ArgsUtils.get('dutyFactor', 0.5, kwargs)
        self._phaseOffset   = float(ArgsUtils.get('phaseOffset', 0.0, kwargs))

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: isHind
    @property
    def isHind(self):
        return self._target not in TargetData._FORE_TARGETS

#___________________________________________________________________________________________________ GS: isLeft
    @property
    def isLeft(self):
        return self._target in TargetData._LEFT_TARGETS

#___________________________________________________________________________________________________ GS: channels
    @property
    def channels(self):
        return self._channels

#___________________________________________________________________________________________________ GS: target
    @property
    def target(self):
        return self._target

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ echo
    def echo(self):
        print 'TARGET:',self.target
        print 'GAIT PHASE OFFSET:',self._phaseOffset
        print 'DUTY FACTOR:',self._dutyFactor
        print 'CHANNELS:'
        for n,v in self._channels.iteritems():
            print v.toString()

#___________________________________________________________________________________________________ createChannel
    def createChannel(self, kind, values =None, times =None):
        dc = DataChannel(
            kind=kind,
            target=self._target,
            times=times,
            values=values
        )
        self._channels[kind] = dc
        return dc

#___________________________________________________________________________________________________ addChannel
    def addChannel(self, channel):
        """Doc..."""
        self._channels[channel.kind] = channel
        return True

#___________________________________________________________________________________________________ getChannel
    def getChannel(self, kind):
        """Doc..."""
        for n,v in self._channels.iteritems():
            if n == kind:
                return v

        return None

#___________________________________________________________________________________________________ createGaitPhaseChannel
    def createGaitPhaseChannel(self, settings):
        """Doc..."""
        steps = int(settings.steps)
        d     = np.zeros(steps)

        for i in range(0, steps):
            cyclePhase = math.modf(float(i)*float(settings.cycles)/float(steps))[0]
            d[i]       = int(cyclePhase <= self._dutyFactor)

        if self._phaseOffset:
            offset = int(round(self._phaseOffset*float(steps)/float(settings.cycles)))
            d      = np.roll(d, offset)

        if settings.cycleOffset:
            offset = int(round(settings.cycleOffset*float(steps)/float(settings.cycles)))
            d      = np.roll(d, offset)

        time = list(np.linspace(settings.startTime, settings.stopTime, steps))

        return self.createChannel(ChannelsEnum.GAIT_PHASE, list(d), time)

#___________________________________________________________________________________________________ createPositionChannel
    def createPositionChannel(self, settings):
        gait = self.getChannel(ChannelsEnum.GAIT_PHASE)
        if not gait:
            return False

        times  = gait.times
        values = gait.values
        steps  = int(settings.steps)
        lifts  = []
        lands  = []

        # Find lift and lands within the step range
        index = 0
        prev  = values[-1]
        while index < steps:
            v = values[index]
            if v - prev < 0:
                lifts.append(index)
            elif v - prev > 0:
                lands.append(index)

            index += 1
            prev   = v

        # Pre-lift or Pre-land
        if lifts[-1] > lands[-1]:
            pre = (-lifts[-1], None)
        else:
            pre = (None, -lands[-1])

        # Post-lift or Post-land
        if lifts[0] < lands[0]:
            post = (lifts[0] + steps - 1, None)
        else:
            post = (None, lands[0] + steps - 1)

        if pre[0] is  None:
            lands.insert(0, pre[1])
        else:
            lifts.insert(0, pre[0])

        if post[0] is None:
            lands.append(post[1])
        else:
            lifts.append(post[0])

        dc             = self.createChannel(kind=ChannelsEnum.POSITION)
        strideLength   = float(settings.configs.get(SkeletonConfigEnum.STRIDE_LENGTH, 50.0))
        strideWidth    = float(settings.configs.get(SkeletonConfigEnum.STRIDE_WIDTH, 50.0))
        positionOffset = settings.configs.get(
            SkeletonConfigEnum.FORE_OFFSET if not self.isHind else SkeletonConfigEnum.HIND_OFFSET,
            Vector3D(0.5*strideWidth, 2*strideLength, 0.0 if self.isHind else 3*strideLength)
        ).clone()

        position = positionOffset.z
        if self.isHind and not self.isLeft:
            position -= 0.5*strideLength

        while lifts or lands:
            if not lifts:
                landed = True
            elif not lands:
                landed = False
            else:
                landed = (lifts[0] > lands[0])

            index  = lands.pop(0) if landed else lifts.pop(0)
            if landed and index > 0:
                position += strideLength

            if index < 0:
                time = times[index] - settings.stopTime
            elif index >= steps:
                time = times[index - steps] + settings.stopTime
            else:
                time = times[index]

            dc.addKeyframe({
                'time':time,
                'value':Vector3D(
                    positionOffset.x*(1.0 if self.isLeft else -1.0),
                    0.0,
                    position),
                'inTangent':TangentsEnum.FLAT,
                'outTangent':TangentsEnum.FLAT,
                'event':('land' if landed else 'lift')
            })

        # Add intermediate aerial keyframes
        prev = dc.keys[0]
        for key in dc.keys[1:]:
            if prev.value.z == key.value.z:
                prev = key
                continue

            dc.addKeyframe({
                'time':prev.time + 0.5*(key.time - prev.time),
                'value':Vector3D(
                    prev.value.x + 0.5*(key.value.x - prev.value.x),
                    0.5*strideWidth,
                    prev.value.z + 0.5*(key.value.z - prev.value.z)
                ),
                'inTangent':[TangentsEnum.LINEAR, TangentsEnum.FLAT, TangentsEnum.SPLINE],
                'outTangent':[TangentsEnum.LINEAR, TangentsEnum.FLAT, TangentsEnum.SPLINE],
                'event':'aerial'
            })
            prev = key

        self.addChannel(dc)

#===================================================================================================
#                                                                               P R O T E C T E D

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
