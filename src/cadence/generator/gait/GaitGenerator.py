# GaitGenerator.py
# (C)2012 http://GaitGenerator.threeaddone.com
# Scott Ernst

import os
import math

import numpy as np

from cadence.config.ConfigReader import ConfigReader
from cadence.config.enum.GaitConfigEnum import GaitConfigEnum
from cadence.config.enum.GeneralConfigEnum import GeneralConfigEnum
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum
from cadence.shared.io.CadenceData import CadenceData
from cadence.util.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ GaitGenerator
class GaitGenerator(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of GaitGenerator."""

        self._configs  = ConfigReader(filenames={
            'general':ArgsUtils.get('generalConfig', 'general/default.cfg', kwargs),
            'gait':ArgsUtils.get('gaitConfig', 'gait/default.cfg', kwargs)
        })
        self._configs.setOverrides(ArgsUtils.get('overrides', None, kwargs))

        self._time = None

        self._leftHind  = dict()
        self._rightHind = dict()

        self._leftFore  = dict()
        self._rightFore = dict()

        self._cycles         = int(self._configs.get(GaitConfigEnum.CYCLES, 1))
        self._cycleOffset    = 0.01*float(self._configs.get(GaitConfigEnum.CYCLE_OFFSET, 0.0))
        self._dutyFactorFore = 0.01*float(self._configs.get(GaitConfigEnum.DUTY_FACTOR_FORE, 50))
        self._dutyFactorHind = 0.01*float(self._configs.get(GaitConfigEnum.DUTY_FACTOR_HIND, 50))
        self._phase          = 0.01*float(self._configs.get(GaitConfigEnum.PHASE))

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: configs
    @property
    def configs(self):
        return self._configs

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        return 'PH-%s_F-%s_H-%s' % (
            str(int(100*self._phase)),
            str(int(100*self._dutyFactorFore)),
            str(int(100*self._dutyFactorHind))
        )

#___________________________________________________________________________________________________ GS: dataFilename
    @property
    def dataFilename(self):
        return self.__class__.__name__ + os.sep + self.name + CadenceData.EXTENSION

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ saveToFile
    def saveToFile(self, filename =None):
        if self._time is None:
            self.run()

        cd = CadenceData(name=self.name, configs=self.configs)

        cd.addChannel(
            'leftHind_grounded', {
                'kind':ChannelsEnum.GAIT_PHASE,
                'target':TargetsEnum.LEFT_HIND,
                'times':self._time,
                'values':self._leftHind[ChannelsEnum.GAIT_PHASE]
            }
        )

        cd.addChannel(
            'leftFore_grounded', {
                'kind':ChannelsEnum.GAIT_PHASE,
                'target':TargetsEnum.LEFT_FORE,
                'times':self._time,
                'values':self._leftFore[ChannelsEnum.GAIT_PHASE]
            }
        )

        cd.addChannel(
            'rightHind_grounded', {
                'kind':ChannelsEnum.GAIT_PHASE,
                'target':TargetsEnum.RIGHT_HIND,
                'times':self._time,
                'values':self._rightHind[ChannelsEnum.GAIT_PHASE]
            }
        )

        cd.addChannel(
            'rightFore_grounded', {
                'kind':ChannelsEnum.GAIT_PHASE,
                'target':TargetsEnum.RIGHT_FORE,
                'times':self._time,
                'values':self._rightFore[ChannelsEnum.GAIT_PHASE]
            }
        )

        cd.write(self.__class__.__name__, name=filename if filename else self.name)

        return True

#___________________________________________________________________________________________________ run
    def run(self):
        """Doc..."""

        steps          = self._configs.get(GeneralConfigEnum.STEPS)
        startTime      = float(self._configs.get(GeneralConfigEnum.START_TIME))
        stopTime       = float(self._configs.get(GeneralConfigEnum.STOP_TIME))

        leftHind  = np.zeros(int(steps))
        leftFore  = np.zeros(int(steps))

        for i in range(0, int(steps)):
            cyclePhase   = math.modf(float(i)*float(self._cycles)/float(steps))[0]
            leftHind[i]  = int(cyclePhase < self._dutyFactorHind)
            leftFore[i]  = int(cyclePhase < self._dutyFactorFore)

        rightHind = np.roll(leftHind, int(round(0.5*float(steps))))
        rightFore = np.roll(leftFore, int(round(float(steps)*(0.75 + self._phase))))
        leftFore  = np.roll(leftFore, int(round(float(steps)*(0.25 + self._phase))))

        if self._cycleOffset:
            offset = int(round(self._cycleOffset*float(steps)/float(self._cycles)))
            leftHind  = np.roll(leftHind, offset)
            rightHind = np.roll(rightHind, offset)
            leftFore  = np.roll(leftFore, offset)
            rightFore = np.roll(rightFore, offset)

        self._leftHind[ChannelsEnum.GAIT_PHASE]  = list(leftHind)
        self._leftFore[ChannelsEnum.GAIT_PHASE]  = list(leftFore)
        self._rightHind[ChannelsEnum.GAIT_PHASE] = list(rightHind)
        self._rightFore[ChannelsEnum.GAIT_PHASE] = list(rightFore)

        self._time = list(np.linspace(startTime, stopTime, steps))

        return True
