# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dec10001-1.ui'
#
# Created: Tue Feb 28 16:50:16 2017
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from Qt import QtCore, QtGui, QtWidgets
import Qt

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayoutWidget = QtWidgets.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 401, 301))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textEdit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_2.addWidget(self.textEdit)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.graphicsView = QtWidgets.QGraphicsView(self.verticalLayoutWidget)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.pinsSpinBox = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        self.pinsSpinBox.setObjectName("pinsSpinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.pinsSpinBox)
        self.addressSpinBox = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        self.addressSpinBox.setMinimum(1)
        self.addressSpinBox.setMaximum(2048)
        self.addressSpinBox.setObjectName("addressSpinBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.addressSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(Qt.QtCompat.translate("Form", "Form", None, -1))
        self.label.setText(Qt.QtCompat.translate("Form", "Accessory Decoder", None, -1))
        self.textEdit.setHtml(Qt.QtCompat.translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.SF NS Text\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Universal accesory and sensor decoder for LocoNet, supporting servo\'s, LED\'s and logic level feedback.</p></body></html>", None, -1))
        self.label_2.setText(Qt.QtCompat.translate("Form", "Address", None, -1))
        self.label_3.setText(Qt.QtCompat.translate("Form", "Pins used", None, -1))

