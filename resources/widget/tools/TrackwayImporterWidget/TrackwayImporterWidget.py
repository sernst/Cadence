# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/scott/Python/Cadence/resources/widget/tools/TrackwayImporterWidget/TrackwayImporterWidget.ui'
#
# Created: Sun Nov 10 00:48:59 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class PySideUiFileSetup(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        Form.loadAllBtn = QtGui.QPushButton(Form)
        Form.loadAllBtn.setGeometry(QtCore.QRect(10, 10, 75, 23))
        Form.loadAllBtn.setObjectName("loadAllBtn")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        Form.loadAllBtn.setText(QtGui.QApplication.translate("Form", "Load All", None, QtGui.QApplication.UnicodeUTF8))

