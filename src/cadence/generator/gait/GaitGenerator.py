# GaitGenerator.py
# (C)2012 http://GaitGenerator.threeaddone.com
# Scott Ernst

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

        self._config  = ConfigReader(configs={
            'general':ArgsUtils.get('generalConfig', 'general/default.cfg', kwargs),
            'gait':ArgsUtils.get('gaitConfig', 'gait/default.cfg', kwargs)
        })

        self._time = None

        self._leftHind  = dict()
        self._rightHind = dict()

        self._leftFore  = dict()
        self._rightFore = dict()

        self._dutyFactorFore = 0.01*float(self._config.get(GaitConfigEnum.DUTY_FACTOR_FORE, 5))
        self._dutyFactorHind = 0.01*float(self._config.get(GaitConfigEnum.DUTY_FACTOR_HIND, 5))
        self._phase          = 0.01*float(self._config.get(GaitConfigEnum.PHASE))

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: config
    @property
    def config(self):
        return self._config

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        return 'p%s_f%s_h%s' % (
            str(self._phase), str(self._dutyFactorFore), str(self._dutyFactorHind)
        )

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ saveToFile
    def saveToFile(self, filename =None):
        if self._time is None:
            self.run()

        cd = CadenceData(name=self.name, configs=self.config)

        cd.addChannel(
            'leftHind_grounded', {
                'kind':ChannelsEnum.GROUNDED,
                'target':TargetsEnum.LEFT_HIND,
                'times':self._time,
                'values':self._leftHind['grounded']
            }
        )

        cd.addChannel(
            'leftFore_grounded', {
                'kind':ChannelsEnum.GROUNDED,
                'target':TargetsEnum.LEFT_FORE,
                'times':self._time,
                'values':self._leftFore['grounded']
            }
        )

        cd.addChannel(
            'rightHind_grounded', {
                'kind':ChannelsEnum.GROUNDED,
                'target':TargetsEnum.RIGHT_HIND,
                'times':self._time,
                'values':self._rightHind['grounded']
            }
        )

        cd.addChannel(
            'rightFore_grounded', {
                'kind':ChannelsEnum.GROUNDED,
                'target':TargetsEnum.RIGHT_HIND,
                'times':self._time,
                'values':self._rightFore['grounded']
            }
        )

        cd.write(self.__class__.__name__, name=filename if filename else self.name)

#___________________________________________________________________________________________________ run
    def run(self):
        """Doc..."""

        steps          = self._config.get(GeneralConfigEnum.STEPS)
        startTime      = float(self._config.get(GeneralConfigEnum.START_TIME))
        stopTime       = float(self._config.get(GeneralConfigEnum.STOP_TIME))

        leftHind  = np.zeros(int(steps))
        leftFore  = np.zeros(int(steps))

        for i in range(0, int(steps)):
            cyclePhase   = float(i)/float(steps)
            leftHind[i]  = int(cyclePhase < self._dutyFactorHind)
            leftFore[i]  = int(cyclePhase < self._dutyFactorFore)

        rightHind = np.roll(leftHind, int(round(0.5*float(steps))))
        rightFore = np.roll(leftFore, int(round(float(steps)*(0.75 + self._phase))))
        leftFore  = np.roll(leftFore, int(round(float(steps)*(0.25 + self._phase))))

        self._leftHind['grounded']  = list(leftHind)
        self._leftFore['grounded']  = list(leftFore)
        self._rightHind['grounded'] = list(rightHind)
        self._rightFore['grounded'] = list(rightFore)

        self._time = list(np.linspace(startTime, stopTime, steps))
