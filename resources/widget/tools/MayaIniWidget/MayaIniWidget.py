# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/scott/Python/Cadence/resources/widget/tools/MayaIniWidget/MayaIniWidget.ui'
#
# Created: Mon Feb 17 16:18:19 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class PySideUiFileSetup(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(608, 422)
        Form.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        Form.verticalLayout_2.setObjectName("verticalLayout_2")
        Form.controlsBox = QtGui.QWidget(Form)
        Form.controlsBox.setObjectName("controlsBox")
        Form.horizontalLayout = QtGui.QHBoxLayout(Form.controlsBox)
        Form.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        Form.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(434, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        Form.horizontalLayout.addItem(spacerItem)
        Form.runBtn = QtGui.QPushButton(Form.controlsBox)
        Form.runBtn.setObjectName("runBtn")
        Form.horizontalLayout.addWidget(Form.runBtn)
        Form.removeBtn = QtGui.QPushButton(Form.controlsBox)
        Form.removeBtn.setObjectName("removeBtn")
        Form.horizontalLayout.addWidget(Form.removeBtn)
        Form.testChk = QtGui.QCheckBox(Form.controlsBox)
        Form.testChk.setObjectName("testChk")
        Form.horizontalLayout.addWidget(Form.testChk)
        Form.verticalLayout_2.addWidget(Form.controlsBox)
        Form.widget_2 = QtGui.QWidget(Form)
        Form.widget_2.setObjectName("widget_2")
        Form.verticalLayout = QtGui.QVBoxLayout(Form.widget_2)
        Form.verticalLayout.setContentsMargins(0, 0, 0, 0)
        Form.verticalLayout.setObjectName("verticalLayout")
        Form.reportTextEdit = QtGui.QTextEdit(Form.widget_2)
        Form.reportTextEdit.setObjectName("reportTextEdit")
        Form.verticalLayout.addWidget(Form.reportTextEdit)
        Form.verticalLayout_2.addWidget(Form.widget_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        Form.runBtn.setText(QtGui.QApplication.translate("Form", "Install", None, QtGui.QApplication.UnicodeUTF8))
        Form.removeBtn.setText(QtGui.QApplication.translate("Form", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        Form.testChk.setText(QtGui.QApplication.translate("Form", "Test Only", None, QtGui.QApplication.UnicodeUTF8))

