# TargetData.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math
from collections import namedtuple

import numpy as np
from pyaid.ArgsUtils import ArgsUtils
from pyaid.dict.DictUtils import DictUtils
from pyaid.string.StringUtils import StringUtils

from cadence.config.enum.SkeletonConfigEnum import SkeletonConfigEnum
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.KeyEventEnum import KeyEventEnum
from cadence.shared.enum.TangentsEnum import TangentsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum
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

    _EXTRAPOLATED_KEY_NTUPLE = namedtuple('ExtrapolatedKey', ['event', 'index'])

#___________________________________________________________________________________________________ __init__
    def __init__(self, target, **kwargs):
        """Creates a new instance of TargetData."""
        self._target        = target
        self._channels      = ArgsUtils.get('channels', dict(), kwargs)
        self._dutyFactor    = ArgsUtils.get('dutyFactor', 0.5, kwargs)
        self._phaseOffset   = float(ArgsUtils.get('phaseOffset', 0.0, kwargs))

        print(self.target, self._phaseOffset)

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
        print('TARGET:',self.target)
        print('GAIT PHASE OFFSET:',self._phaseOffset)
        print('DUTY FACTOR:',self._dutyFactor)
        print('CHANNELS:')
        for n,v in DictUtils.iter(self._channels):
            print(v.toString())

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
        for n,v in DictUtils.iter(self._channels):
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
        cls  = self.__class__
        gait = self.getChannel(ChannelsEnum.GAIT_PHASE)
        if not gait:
            return False

        #-------------------------------------------------------------------------------------------
        # INITIALIZATION
        dc             = self.createChannel(kind=ChannelsEnum.POSITION)
        times          = gait.times
        values         = gait.values
        steps          = int(settings.steps)
        lifts          = []
        lands          = []
        strideLength   = float(settings.configs.get(SkeletonConfigEnum.STRIDE_LENGTH, 50.0))
        strideWidth    = float(settings.configs.get(SkeletonConfigEnum.STRIDE_WIDTH, 50.0))
        hindOffset     = settings.configs.get(
            SkeletonConfigEnum.HIND_OFFSET,
            Vector3D(0.5*strideWidth, 2.0*strideLength, 0.0)
        ).clone()
        foreOffset     = settings.configs.get(
            SkeletonConfigEnum.FORE_OFFSET,
            Vector3D(0.5*strideWidth, 2.0*strideLength, 3.0*strideLength)
        ).clone()
        backLength     = foreOffset.z - hindOffset.z
        positionOffset = hindOffset if self.isHind else foreOffset

        position = math.modf(self._phaseOffset)[0]*strideLength
        if not self.isHind:
            position += backLength

        #-------------------------------------------------------------------------------------------
        # FIND POSITION KEYFRAMES
        #       Find lift and lands within the step range by finding changes in the gait-phase
        #       channel.
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

        # PRE KEY
        preEvent = KeyEventEnum.LIFT if lifts[0] > lands[0] else KeyEventEnum.LAND
        src      = lifts if preEvent == KeyEventEnum.LIFT else lands
        pre      = cls._EXTRAPOLATED_KEY_NTUPLE(
            event=preEvent,
            index=-src[-1] if len(src) == 1 else (src[0] - (src[1] - src[0]))
        )

        # POST KEY
        postEvent = KeyEventEnum.LIFT if lifts[-1] < lands[-1] else KeyEventEnum.LAND
        src       = lifts if postEvent == KeyEventEnum.LIFT else lands
        post      = cls._EXTRAPOLATED_KEY_NTUPLE(
            event=postEvent,
            index=(src[0] + steps - 1) if len(src) == 1 else (src[-1] + (src[-1] - src[-2]))
        )

        if pre.event == KeyEventEnum.LAND:
            lands.insert(0, pre.index)
            position -= strideLength
        else:
            lifts.insert(0, pre.index)

        if post.event == KeyEventEnum.LAND:
            lands.append(post.index)
        else:
            lifts.append(post.index)

        #-------------------------------------------------------------------------------------------
        # CREATE KEYFRAMES
        #       From parsed gait-phase channel, create lift and land keyframes.
        while lifts or lands:
            if not lifts:
                landed = True
            elif not lands:
                landed = False
            else:
                landed = (lifts[0] > lands[0])

            index  = lands.pop(0) if landed else lifts.pop(0)
            if landed:
                if len(dc.keys) > 0:
                    position += strideLength
            else:
                if index < 0:
                    position -= strideLength

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
                'event':(KeyEventEnum.LAND if landed else KeyEventEnum.LIFT)
            })

        #-------------------------------------------------------------------------------------------
        # AERIAL KEYS
        #       Inserts intermediate aerial keyframes between lift and land keyframes.
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
                'event':KeyEventEnum.AERIAL
            })
            prev = key

        #-------------------------------------------------------------------------------------------
        # AERIAL PRE-KEY
        #       Handles the case where the first keyframe should be an aerial to ensure correct
        #       display at startTime.
        key = dc.keys[0]
        if key.event == 'land' and key.time > settings.startTime:
            time = 0.5*(1.0 - self._dutyFactor)*(settings.stopTime - settings.startTime)
            dc.addKeyframe({
                'time':key.time - time,
                'value':Vector3D(
                    key.value.x,
                    0.5*strideWidth,
                    key.value.z - strideLength
                ),
                'inTangent':[TangentsEnum.LINEAR, TangentsEnum.FLAT, TangentsEnum.SPLINE],
                'outTangent':[TangentsEnum.LINEAR, TangentsEnum.FLAT, TangentsEnum.SPLINE],
                'event':KeyEventEnum.AERIAL
            })

        dc.echo()
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
        return StringUtils.toUnicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
