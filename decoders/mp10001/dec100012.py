# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pinconfform.ui'
#
# Created: Tue Feb 28 16:51:37 2017
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
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.stackedWidget = QtWidgets.QStackedWidget(Form)
        self.stackedWidget.setGeometry(QtCore.QRect(-1, -1, 401, 301))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.formLayoutWidget = QtWidgets.QWidget(self.page)
        self.formLayoutWidget.setGeometry(QtCore.QRect(-1, 10, 401, 222))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_10 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.comboBox_3 = QtWidgets.QComboBox(self.formLayoutWidget)
        self.comboBox_3.setObjectName("comboBox_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox_3)
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label)
        self.LNAddressSpinBox1 = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.LNAddressSpinBox1.setMinimum(1)
        self.LNAddressSpinBox1.setMaximum(2048)
        self.LNAddressSpinBox1.setObjectName("LNAddressSpinBox1")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.LNAddressSpinBox1)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.ArduinoPinSpinBox1 = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.ArduinoPinSpinBox1.setMinimum(1)
        self.ArduinoPinSpinBox1.setMaximum(12)
        self.ArduinoPinSpinBox1.setObjectName("ArduinoPinSpinBox1")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.ArduinoPinSpinBox1)
        self.label_3 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.pos1SpinBox = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.pos1SpinBox.setMinimum(900)
        self.pos1SpinBox.setMaximum(2100)
        self.pos1SpinBox.setProperty("value", 1500)
        self.pos1SpinBox.setObjectName("pos1SpinBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.pos1SpinBox)
        self.label_4 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.pos2SpinBox = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.pos2SpinBox.setMinimum(900)
        self.pos2SpinBox.setMaximum(2100)
        self.pos2SpinBox.setProperty("value", 1500)
        self.pos2SpinBox.setObjectName("pos2SpinBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.pos2SpinBox)
        self.label_5 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.speedSpinBox = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.speedSpinBox.setMinimum(1)
        self.speedSpinBox.setMaximum(255)
        self.speedSpinBox.setSingleStep(10)
        self.speedSpinBox.setObjectName("speedSpinBox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.speedSpinBox)
        self.pos1Button = QtWidgets.QPushButton(self.page)
        self.pos1Button.setGeometry(QtCore.QRect(110, 230, 121, 32))
        self.pos1Button.setObjectName("pos1Button")
        self.pos2Button = QtWidgets.QPushButton(self.page)
        self.pos2Button.setGeometry(QtCore.QRect(230, 230, 113, 32))
        self.pos2Button.setObjectName("pos2Button")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.page_2)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 401, 301))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_7 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_7.setObjectName("label_7")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.label_8 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_8.setObjectName("label_8")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.ArduinoPinSpinBox2 = QtWidgets.QSpinBox(self.formLayoutWidget_2)
        self.ArduinoPinSpinBox2.setMinimum(1)
        self.ArduinoPinSpinBox2.setMaximum(12)
        self.ArduinoPinSpinBox2.setObjectName("ArduinoPinSpinBox2")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.ArduinoPinSpinBox2)
        self.ledEffectComboBox = QtWidgets.QComboBox(self.formLayoutWidget_2)
        self.ledEffectComboBox.setObjectName("ledEffectComboBox")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.ledEffectComboBox)
        self.label_9 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_9.setObjectName("label_9")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.label_6 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_6.setObjectName("label_6")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.LNAddressSpinBox2 = QtWidgets.QSpinBox(self.formLayoutWidget_2)
        self.LNAddressSpinBox2.setMinimum(1)
        self.LNAddressSpinBox2.setMaximum(2048)
        self.LNAddressSpinBox2.setObjectName("LNAddressSpinBox2")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.LNAddressSpinBox2)
        self.comboBox_2 = QtWidgets.QComboBox(self.formLayoutWidget_2)
        self.comboBox_2.setObjectName("comboBox_2")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox_2)
        self.ledValue1pinBox = QtWidgets.QSpinBox(self.formLayoutWidget_2)
        self.ledValue1pinBox.setObjectName("ledValue1pinBox")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.ledValue1pinBox)
        self.ledValue2SpinBox = QtWidgets.QSpinBox(self.formLayoutWidget_2)
        self.ledValue2SpinBox.setObjectName("ledValue2SpinBox")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.ledValue2SpinBox)
        self.label_11 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_11.setObjectName("label_11")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.label_12 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_12.setObjectName("label_12")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_12)
        self.stackedWidget.addWidget(self.page_2)

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(Qt.QtCompat.translate("Form", "Form", None, -1))
        self.label_10.setText(Qt.QtCompat.translate("Form", "Pin function", None, -1))
        self.label.setText(Qt.QtCompat.translate("Form", "LocoNet address", None, -1))
        self.label_2.setText(Qt.QtCompat.translate("Form", "Arduino pin", None, -1))
        self.label_3.setText(Qt.QtCompat.translate("Form", "Position 1", None, -1))
        self.label_4.setText(Qt.QtCompat.translate("Form", "Position 2", None, -1))
        self.label_5.setText(Qt.QtCompat.translate("Form", "Speed", None, -1))
        self.pos1Button.setText(Qt.QtCompat.translate("Form", "Pos 1 (Straight)", None, -1))
        self.pos2Button.setText(Qt.QtCompat.translate("Form", "Pos 2 (Thrown)", None, -1))
        self.label_7.setText(Qt.QtCompat.translate("Form", "Arduino Pin", None, -1))
        self.label_8.setText(Qt.QtCompat.translate("Form", "LED effect", None, -1))
        self.label_9.setText(Qt.QtCompat.translate("Form", "Pin function", None, -1))
        self.label_6.setText(Qt.QtCompat.translate("Form", "LocoNet address", None, -1))
        self.label_11.setText(Qt.QtCompat.translate("Form", "Effect value 1", None, -1))
        self.label_12.setText(Qt.QtCompat.translate("Form", "Effect value 2", None, -1))

