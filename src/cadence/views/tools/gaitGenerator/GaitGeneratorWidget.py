# GaitGeneratorWidget.py
# (C)2012 http://cadence.ThreeAddOne.com
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide.QtCore import *
from pyaid.string.StringUtils import StringUtils
from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.config.enum.GaitConfigEnum import GaitConfigEnum
from cadence.config.enum.SkeletonConfigEnum import SkeletonConfigEnum
from cadence.generator.gait.GaitGenerator import GaitGenerator
from cadence.mayan.gait.GaitVisualizer import GaitVisualizer
from cadence.util.math3D.Vector3D import Vector3D


#_______________________________________________________________________________
class GaitGeneratorWidget(PyGlassWidget):

#===============================================================================
#                                                                                       C L A S S

    RESOURCE_FOLDER_PREFIX = ['tools']

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        super(GaitGeneratorWidget, self).__init__(parent, **kwargs)

        w = self
        w.gadLengthLabel.setText(StringUtils.toUnicode(w.gadLengthSlider.value()))
        w.gadLengthSlider.valueChanged.connect(w.gadLengthLabel.setNum)

        w.gaitPhaseLabel.setText(StringUtils.toUnicode(w.gaitPhaseSlider.value()))
        w.gaitPhaseSlider.valueChanged.connect(w.gaitPhaseLabel.setNum)

        w.stepLengthLabel.setText(StringUtils.toUnicode(w.stepLengthSlider.value()))
        QObject.connect(w.stepLengthSlider, SIGNAL("valueChanged(int)"), w.stepLengthLabel.setNum)

        w.dutyFactorHindLabel.setText(StringUtils.toUnicode(w.dutyFactorHindSlider.value()))
        QObject.connect(w.dutyFactorHindSlider, SIGNAL("valueChanged(int)"), w.dutyFactorHindLabel.setNum)

        w.dutyFactorForeLabel.setText(StringUtils.toUnicode(w.dutyFactorForeSlider.value()))
        QObject.connect(w.dutyFactorForeSlider, SIGNAL("valueChanged(int)"), w.dutyFactorForeLabel.setNum)

        w.cyclesLabel.setText(StringUtils.toUnicode(w.cyclesSlider.value()))
        QObject.connect(w.cyclesSlider, SIGNAL("valueChanged(int)"), w.cyclesLabel.setNum)

        w.runButton.clicked.connect(self._runGaitGeneration)

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _runGaitGeneration(self):
        w = self
        gg = GaitGenerator(
            overrides = {
                GaitConfigEnum.CYCLES:w.cyclesSlider.value(),
                GaitConfigEnum.DUTY_FACTOR_HIND:w.dutyFactorHindSlider.value(),
                GaitConfigEnum.DUTY_FACTOR_FORE:w.dutyFactorForeSlider.value(),
                GaitConfigEnum.PHASE:w.gaitPhaseSlider.value(),
                SkeletonConfigEnum.STRIDE_LENGTH:w.stepLengthSlider.value(),
                SkeletonConfigEnum.FORE_OFFSET:Vector3D(None, None, float(w.gadLengthSlider.value()))
            }
        )
        gg.run()

        gv = GaitVisualizer(data=gg.toCadenceData())
        gv.buildScene()

