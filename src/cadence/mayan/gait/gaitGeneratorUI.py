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
from cadence.util.math3D.Vector3D import Vector3D

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

        w.gadLengthLabel.setText(unicode(w.gadLengthSlider.value()))
        QObject.connect(w.gadLengthSlider, SIGNAL("valueChanged(int)"), w.gadLengthLabel.setNum)

        w.gaitPhaseLabel.setText(unicode(w.gaitPhaseSlider.value()))
        QObject.connect(w.gaitPhaseSlider, SIGNAL("valueChanged(int)"), w.gaitPhaseLabel.setNum)

        w.stepLengthLabel.setText(unicode(w.stepLengthSlider.value()))
        QObject.connect(w.stepLengthSlider, SIGNAL("valueChanged(int)"), w.stepLengthLabel.setNum)

        w.dutyFactorHindLabel.setText(unicode(w.dutyFactorHindSlider.value()))
        QObject.connect(w.dutyFactorHindSlider, SIGNAL("valueChanged(int)"), w.dutyFactorHindLabel.setNum)

        w.dutyFactorForeLabel.setText(unicode(w.dutyFactorForeSlider.value()))
        QObject.connect(w.dutyFactorForeSlider, SIGNAL("valueChanged(int)"), w.dutyFactorForeLabel.setNum)

        w.cyclesLabel.setText(unicode(w.cyclesSlider.value()))
        QObject.connect(w.cyclesSlider, SIGNAL("valueChanged(int)"), w.cyclesLabel.setNum)

        w.runButton.clicked.connect(self._runGaitGeneration)

        self.adjustSize()

#___________________________________________________________________________________________________ sizeHint
    def sizeHint(self, *args, **kwargs):
        size = QWidget.sizeHint(self)
        size.setWidth(self.myWidget.baseSize().width())
        size.setHeight(self.myWidget.baseSize().height())
        return size

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _runGaitGeneration
    def _runGaitGeneration(self):
        w = self.myWidget
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

#===================================================================================================
#                                                                                     M O D U L E

app = QApplication(sys.argv)
win = Viewer()
win.show()

app.exec_()
sys.exit()
