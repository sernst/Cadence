# gaitGeneratorUI.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import sys

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import QUiLoader

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.config.enum.GaitConfigEnum import GaitConfigEnum
from cadence.config.enum.SkeletonConfigEnum import SkeletonConfigEnum
from cadence.generator.gait.GaitGenerator import GaitGenerator
from cadence.mayan.gait.GaitVisualizer import GaitVisualizer

#___________________________________________________________________________________________________ Viewer
class Viewer(QWidget):

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        QWidget.__init__(self)
        l = QUiLoader()
        file = QFile(CadenceEnvironment.getResourcePath('gui', 'GaitGeneratorUI.ui'))
        file.open(QFile.ReadOnly)
        myWidget = l.load(file, self)
        file.close()

        layout = QVBoxLayout()
        layout.addWidget(myWidget)
        self.setLayout(layout)

        self.widgets = []
        for item in dir(myWidget):
            item = getattr(myWidget, item)
            if isinstance(item, QWidget):
                self.widgets.append(item)

        w             = myWidget
        self.myWidget = myWidget

        w.gaitPhaseLabel.setText(unicode(w.gaitPhaseSlider.value()))
        QObject.connect(w.gaitPhaseSlider, SIGNAL("valueChanged(int)"), w.gaitPhaseLabel.setNum)

        w.strideLengthLabel.setText(unicode(w.strideLengthSlider.value()))
        QObject.connect(w.strideLengthSlider, SIGNAL("valueChanged(int)"), w.strideLengthLabel.setNum)

        w.dutyFactorHindLabel.setText(unicode(w.dutyFactorHindSlider.value()))
        QObject.connect(w.dutyFactorHindSlider, SIGNAL("valueChanged(int)"), w.dutyFactorHindLabel.setNum)

        w.dutyFactorForeLabel.setText(unicode(w.dutyFactorForeSlider.value()))
        QObject.connect(w.dutyFactorForeSlider, SIGNAL("valueChanged(int)"), w.dutyFactorForeLabel.setNum)

        w.cyclesLabel.setText(unicode(w.cyclesSlider.value()))
        QObject.connect(w.cyclesSlider, SIGNAL("valueChanged(int)"), w.cyclesLabel.setNum)

        w.runButton.clicked.connect(self._runGaitGeneration)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _runGaitGeneration
    def _runGaitGeneration(self):
        gg = GaitGenerator(
            overrides = {
                GaitConfigEnum.CYCLES:self.myWidget.cyclesSlider.value(),
                GaitConfigEnum.DUTY_FACTOR_HIND:self.myWidget.dutyFactorHindSlider.value(),
                GaitConfigEnum.DUTY_FACTOR_FORE:self.myWidget.dutyFactorForeSlider.value(),
                GaitConfigEnum.PHASE:self.myWidget.gaitPhaseSlider.value(),
                SkeletonConfigEnum.STRIDE_LENGTH:self.myWidget.strideLengthSlider.value()
            }
        )
        gg.run()

        gv = GaitVisualizer(data=gg.toCadenceData())
        gv.buildScene()

#===================================================================================================
#                                                                                     M O D U L E

app = QApplication(sys.argv)
win = Viewer()
win.show()

app.exec_()
sys.exit()
