import os

from Qt import QtCompat, QtGui, QtWidgets


class PinConfigWidget(QtWidgets.QWidget):
    cvsPerPin = 10

    def __init__(self, index, decoder):
        super(PinConfigWidget, self).__init__()
        self.decoder = decoder
        self.index = index

        plugin_directory = os.path.dirname(os.path.abspath(__file__))
        self.ui = QtCompat.loadUi(os.path.join(plugin_directory, "pinconfform.ui"))
        self.ui.stackedWidget.setCurrentIndex(0)

        for i in ["Servo", "LED"]:
            self.ui.comboBox_3.addItem(i)
            self.ui.comboBox_2.addItem(i)

        self.ui.comboBox_2.currentIndexChanged.connect(self.functionChanged)
        self.ui.comboBox_3.currentIndexChanged.connect(self.functionChanged)

        self.ui.LNAddressSpinBox1.valueChanged.connect(self.lnaddressChanged)
        self.ui.LNAddressSpinBox2.valueChanged.connect(self.lnaddressChanged)

        self.ui.ArduinoPinSpinBox1.valueChanged.connect(self.arduinopinChanged)
        self.ui.ArduinoPinSpinBox2.valueChanged.connect(self.arduinopinChanged)

        self.ui.pos1SpinBox.valueChanged.connect(self.pos1Changed)
        self.ui.pos2SpinBox.valueChanged.connect(self.pos2Changed)
        self.ui.speedSpinBox.valueChanged.connect(self.speedChanged)

        self.decoder.dataChanged.connect(self.cvDataChanged)

    def cvDataChanged(self, topleft, bottomright):
        cv = self.decoder.row2cv(topleft.row())
        value = self.decoder.data(topleft)

        if cv > 31:
            pinconf = int((cv - 32) / self.cvsPerPin)
            pincv = (cv - 32) - (pinconf * self.cvsPerPin)
            print("CV: ", cv, " Pin CV: ", pincv, " Value: ", value)
            try:
                value = int(value)
            except ValueError:
                return

            if pincv == 1:
                self.ui.LNAddressSpinBox1.setValue(value)
                self.ui.LNAddressSpinBox2.setValue(value)
            if pincv == 0:
                self.ui.arduinopinSpinBox1.setValue(value)
                self.ui.arduinopinSpinBox2.setValue(value)
            if pincv == 2:
                self.ui.pos1SpinBox.setValue(value)
                self.ui.ledValue1SpinBox.setValue(value)
            if pincv == 3:
                self.ui.pos2SpinBox.setValue(value)
                self.ui.ledValue2SpinBox.setValue(value)
            if pincv == 4:
                self.ui.speedSpinBox.setValue(value)
                self.ui.ledEffectComboBox.setValue(value)


    def functionChanged(self, index):
        cv = self.index + 9
        value = index
        self.ui.stackedWidget.setCurrentIndex(value)
        self.ui.comboBox_2.setCurrentIndex(value)
        self.ui.comboBox_3.setCurrentIndex(value)
        if index == 0:
            value = 2
        self.decoder.writeCV(cv, value)

    def arduinopinChanged(self, index):
        cv = (self.index) * 10 + 32
        value = index
        self.ui.ArduinoPinSpinBox1.setValue(value)
        self.ui.ArduinoPinSpinBox2.setValue(value)
        self.decoder.writeCV(cv, value)

    def lnaddressChanged(self, index):
        cv = (self.index) * 10 + 33
        value = index
        self.decoder.writeCV(cv, value)

    def pos1Changed(self, index):
        cv = (self.index) * 10 + 34
        value = index
        self.decoder.writeCV(cv, value)

    def pos2Changed(self, index):
        cv = (self.index) * 10 + 35
        value = index
        self.decoder.writeCV(cv, value)

    def speedChanged(self, index):
        cv = (self.index) * 10 + 36
        value = index
        self.decoder.writeCV(cv, value)


    def setupNoneLayout(self):
        NoneLayout = QtGui.QWidget()
        NoneLayout.formlayout = QtGui.QFormLayout(NoneLayout)
        NoneLayout.formlayout.setContentsMargins(0, 0, 0, 0)
        NoneLayout.formlayout.setObjectName("NoneLayout")


    def setupServoLayout(self):
        ServoLayout = QtGui.QWidget()
        ServoLayout.formlayout = QtGui.QFormLayout(ServoLayout)
        ServoLayout.formlayout.setContentsMargins(0, 0, 0, 0)
        ServoLayout.formlayout.setObjectName("ServoLayout")

        ServoLayout.pos1label = QtGui.QLabel(ServoLayout)
        ServoLayout.pos1label.setObjectName("Pos1label")
        ServoLayout.pos1label.setText("Servo Pos 1")
        ServoLayout.formlayout.setWidget(3, QtGui.QFormLayout.LabelRole, ServoLayout.pos1label)

        ServoLayout.pos1SpinBox = QtGui.QSpinBox(ServoLayout)
        ServoLayout.pos1SpinBox.setObjectName("Pos1SpinBox")
        ServoLayout.formlayout.setWidget(3, QtGui.QFormLayout.FieldRole, ServoLayout.pos1SpinBox)
        ServoLayout.pos1SpinBox.valueChanged.connect(self.pos1Changed)

        ServoLayout.pos2label = QtGui.QLabel(ServoLayout)
        ServoLayout.pos2label.setObjectName("Pos2label")
        ServoLayout.pos2label.setText("Servo Pos 2")
        ServoLayout.formlayout.setWidget(4, QtGui.QFormLayout.LabelRole, ServoLayout.pos2label)

        ServoLayout.pos2SpinBox = QtGui.QSpinBox(ServoLayout)
        ServoLayout.pos2SpinBox.setObjectName("Pos2SpinBox")
        ServoLayout.formlayout.setWidget(4, QtGui.QFormLayout.FieldRole, ServoLayout.pos2SpinBox)
        ServoLayout.pos2SpinBox.valueChanged.connect(self.pos2Changed)

        # ServoLayout.currentFunctionWidgets.append(ServoLayout.pos1label)
        # ServoLayout.currentFunctionWidgets.append(ServoLayout.pos1SpinBox)
        # ServoLayout.currentFunctionWidgets.append(ServoLayout.pos2label)
        # ServoLayout.currentFunctionWidgets.append(ServoLayout.pos2SpinBox)

        return ServoLayout


    def addFunctionWidgets(self, function):
        # if function == 1:
        pass


class dec10001controller(object):
    """docstring for dec10001controller"""

    def __init__(self, decoder, tabwidget):
        super(dec10001controller, self).__init__()
        self.decoder = decoder
        self.tabwidget = tabwidget

        self.generalwidget = QtWidgets.QWidget()

        plugin_directory = os.path.dirname(os.path.abspath(__file__))
        self.ui = QtCompat.loadUi(os.path.join(plugin_directory, "dec10001-1.ui"))
        # self.ui.show()
        # self.ui.setupUi(self.generalwidget)

        self.tabs = []
        self.tabs.append(self.tabwidget.addTab(self.ui, "Dec 10001"))
        self.pin_widgets = []

        address = self.decoder.getCV(1)
        if address is None:
            address = 1

        self.ui.addressSpinBox.setRange(1, 255)
        try:
            self.ui.addressSpinBox.setValue(int(address))
        except ValueError:
            pass
        self.ui.addressSpinBox.valueChanged.connect(self.addressChanged)

        confpins = self.decoder.getCV(6)
        if confpins is None:
            confpins = 0

        try:
            for slot in range(int(confpins)):
                self.pin_widgets.append(PinConfigWidget(slot, self.decoder))
                self.tabs.append(self.tabwidget.addTab(self.pin_widgets[-1].ui, "Slot {}".format(slot)))
        except ValueError as e:
            print(e)

        self.ui.pinsSpinBox.lineEdit().setReadOnly(True)
        try:
            self.ui.pinsSpinBox.setValue(int(confpins))
        except ValueError:
            pass
        self.ui.pinsSpinBox.valueChanged.connect(self.confpinsChanged)
        self.decoder.dataChanged.connect(self.cvChange)

    def cvChange(self, cv, value):
        # cv = #self.decoder.row2cv(topleft.row())
        # value = self.decoder.data(topleft)
        if value is None:
            return
        if cv == 1:
            self.ui.addressSpinBox.setValue(int(value))
        elif cv == 6:
            self.ui.pinsSpinBox.setValue(int(value))

    def addressChanged(self, value):
        """docstring for addressChanged"""
        self.decoder.writeCV(1, value)

    def generalCVs(self):
        return range(1, 31)

    def confpinsChanged(self, value):
        """docstring for confpinsChanged"""
        self.decoder.writeCV(6, value)
        while len(self.tabs) < value + 1:
            self.pin_widgets.append(PinConfigWidget(len(self.tabs) - 1, self.decoder))
            self.tabs.append(self.tabwidget.addTab(self.pin_widgets[-1].ui, "Slot {}".format(len(self.tabs) - 1)))
            print(self.tabs)

        if len(self.tabs) > (value + 1):
            self.tabwidget.removeTab(self.tabs[-1])
            self.tabs.remove(self.tabs[-1])

        print("tabs: {}".format(self.tabs))
        print(value)

    def close(self):
        print("closing tabs: {}".format(self.tabs))
        for tab in self.tabs[::-1]:
            self.tabwidget.removeTab(tab)
            # self.tabs.remove(tab)