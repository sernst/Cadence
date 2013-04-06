# GaitGenerator.py
# (C)2012 http://GaitGenerator.threeaddone.com
# Scott Ernst

import os

from pyaid.ArgsUtils import ArgsUtils

from cadence.config.ConfigReader import ConfigReader
from cadence.config.enum.GaitConfigEnum import GaitConfigEnum
from cadence.config.enum.GeneralConfigEnum import GeneralConfigEnum
from cadence.shared.data.TargetData import TargetData
from cadence.shared.enum.TargetsEnum import TargetsEnum
from cadence.shared.io.CadenceData import CadenceData

#___________________________________________________________________________________________________ GaitGenerator
class GaitGenerator(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """ Creates a new instance of GaitGenerator.
            @@@param generalConfig:string
                Relative path to the general configuration file within the Cadence/config directory.

            @@@param gaitConfig:string
                Relative path to the gait configuration file within the Cadence/config directory.
        """

        self._configs  = ConfigReader(
            filenames={
                'general':ArgsUtils.get('generalConfig', 'general/default.cfg', kwargs),
                'gait':ArgsUtils.get('gaitConfig', 'gait/default.cfg', kwargs),
                'skeleton':ArgsUtils.get('skeletonConfig', 'skeleton/default.cfg', kwargs)
            },
            overrides=ArgsUtils.get('overrides', None, kwargs)
        )

        self._cycles         = int(self._configs.get(GaitConfigEnum.CYCLES, 1))
        self._cycleOffset    = 0.01*float(self._configs.get(GaitConfigEnum.CYCLE_OFFSET, 0.0))
        self._steps          = self._cycles*int(self._configs.get(GeneralConfigEnum.STEPS))
        self._startTime      = float(self._configs.get(GeneralConfigEnum.START_TIME))
        self._stopTime       = float(self._cycles)*float(self._configs.get(GeneralConfigEnum.STOP_TIME))

        self._dutyFactorFore = 0.01*float(self._configs.get(GaitConfigEnum.DUTY_FACTOR_FORE, 50))
        self._dutyFactorHind = 0.01*float(self._configs.get(GaitConfigEnum.DUTY_FACTOR_HIND, 50))
        self._phase          = 0.01*float(self._configs.get(GaitConfigEnum.PHASE))

        self._leftHind  = TargetData(
            TargetsEnum.LEFT_HIND,
            dutyFactor=self._dutyFactorHind
        )

        self._rightHind = TargetData(
            TargetsEnum.RIGHT_HIND,
            dutyFactor=self._dutyFactorHind,
            phaseOffset=0.5
        )

        self._leftFore  = TargetData(
            TargetsEnum.LEFT_FORE,
            dutyFactor=self._dutyFactorFore,
            phaseOffset=self._phase
        )

        self._rightFore = TargetData(
            TargetsEnum.RIGHT_FORE,
            dutyFactor=self._dutyFactorFore,
            phaseOffset=0.5 + self._phase
        )

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: cycles
    @property
    def cycles(self):
        return self._cycles

#___________________________________________________________________________________________________ GS: cycleOffset
    @property
    def cycleOffset(self):
        return self._cycleOffset

#___________________________________________________________________________________________________ GS: steps
    @property
    def steps(self):
        return self._steps

#___________________________________________________________________________________________________ GS: startTime
    @property
    def startTime(self):
        return self._startTime

#___________________________________________________________________________________________________ GS: stopTime
    @property
    def stopTime(self):
        return self._stopTime

#___________________________________________________________________________________________________ GS: phase
    @property
    def phase(self):
        return self._phase

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

#___________________________________________________________________________________________________ echo
    def echo(self):
        print '\n', 100*'=','GAIT GENERATION RESULTS:'
        print 100*'-', 'LEFT HIND:'
        print self._leftHind.echo()
        print 100*'-', 'LEFT FORE:'
        print self._leftFore.echo()
        print 100*'-', 'RIGHT FORE:'
        print self._rightFore.echo()
        print 100*'-', 'RIGHT HIND:'
        print self._rightHind.echo()

#___________________________________________________________________________________________________ toCadenceData
    def toCadenceData(self):
        cd = CadenceData(name=self.name, configs=self.configs)
        cd.addChannels(self._leftHind.channels)
        cd.addChannels(self._leftFore.channels)
        cd.addChannels(self._rightHind.channels)
        cd.addChannels(self._rightFore.channels)
        return cd

#___________________________________________________________________________________________________ saveToFile
    def saveToFile(self, filename =None):
        cd = self.toCadenceData()
        cd.write(self.__class__.__name__, name=filename if filename else self.name)
        return True

#___________________________________________________________________________________________________ run
    def run(self):
        """Doc..."""
        if not self._generateGaitPhases():
            return False

        if not self._generatePositions():
            return False

        return True

#___________________________________________________________________________________________________ _generateGaitPhases
    def _generateGaitPhases(self):
        self._leftHind.createGaitPhaseChannel(self)
        self._leftFore.createGaitPhaseChannel(self)
        self._rightHind.createGaitPhaseChannel(self)
        self._rightFore.createGaitPhaseChannel(self)
        return True

#___________________________________________________________________________________________________ _generatePositions
    def _generatePositions(self):
        self._leftHind.createPositionChannel(self)
        self._leftFore.createPositionChannel(self)
        self._rightHind.createPositionChannel(self)
        self._rightFore.createPositionChannel(self)
        return True
