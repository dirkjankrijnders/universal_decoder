# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'infodialog.ui'
#
# Created: Tue Feb 28 15:55:07 2017
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from Qt import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.tableView = QtWidgets.QTableView(Dialog)
        self.tableView.setGeometry(QtCore.QRect(10, 10, 381, 221))
        self.tableView.setObjectName("tableView")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(Qt.QtCompat.translate("Dialog", "Dialog", None, -1))

