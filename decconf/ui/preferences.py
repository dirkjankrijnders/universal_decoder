# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences.ui'
#
# Created: Tue Mar  8 17:27:06 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(386, 161)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 120, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.deviceCombo = QtGui.QComboBox(Dialog)
        self.deviceCombo.setGeometry(QtCore.QRect(163, 20, 211, 26))
        self.deviceCombo.setObjectName("deviceCombo")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 20, 101, 16))
        self.label.setObjectName("label")
        self.connectCheckBox = QtGui.QCheckBox(Dialog)
        self.connectCheckBox.setGeometry(QtCore.QRect(30, 60, 111, 20))
        self.connectCheckBox.setObjectName("connectCheckBox")
        self.detectCheckBox = QtGui.QCheckBox(Dialog)
        self.detectCheckBox.setGeometry(QtCore.QRect(30, 90, 111, 20))
        self.detectCheckBox.setObjectName("detectCheckBox")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Default device:", None, QtGui.QApplication.UnicodeUTF8))
        self.connectCheckBox.setText(QtGui.QApplication.translate("Dialog", "Auto connect", None, QtGui.QApplication.UnicodeUTF8))
        self.detectCheckBox.setText(QtGui.QApplication.translate("Dialog", "Auto detect", None, QtGui.QApplication.UnicodeUTF8))

