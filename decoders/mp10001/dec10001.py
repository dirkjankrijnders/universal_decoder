import os

from Qt import QtCompat, QtWidgets


class PinConfigWidget(QtWidgets.QWidget):
    cvsPerPin = 10
    function_map = {2: 0, 3: 1, 1: 2, 0: 1, 102: 3, '': 4}

    def slot_parameter_to_cv(self, parameter, slot=None):
        if slot is None:
            slot = self.index
        return slot * self.cvsPerPin + 32 + parameter

    def __init__(self, index, decoder):
        super(PinConfigWidget, self).__init__()
        self.decoder = decoder
        self.index = index

        plugin_directory = os.path.dirname(os.path.abspath(__file__))
        self.ui = QtCompat.loadUi(os.path.join(plugin_directory, "pinconfform.ui"))
        self.ui.stackedWidget.setCurrentIndex(0)

        for i in ["Servo", "LED", "Input", "PCA Servo", "N/A"]:
            self.ui.comboBox_3.addItem(i)
            self.ui.comboBox_2.addItem(i)
            self.ui.comboBox_4.addItem(i)

        self.ui.comboBox_2.setCurrentIndex(self.function_map[self.decoder.CVs[9 + self.index]])
        self.ui.comboBox_3.setCurrentIndex(self.function_map[self.decoder.CVs[9 + self.index]])
        self.ui.comboBox_4.setCurrentIndex(self.function_map[self.decoder.CVs[9 + self.index]])
        self.ui.comboBox_2.currentIndexChanged.connect(self.functionChanged)
        self.ui.comboBox_3.currentIndexChanged.connect(self.functionChanged)
        self.ui.comboBox_4.currentIndexChanged.connect(self.functionChanged)
        self.functionChanged()

        self.ui.LNAddressSpinBox1.setValue(self.cv(0))
        self.ui.LNAddressSpinBox2.setValue(self.cv(0))
        self.ui.LNAddressSpinBox3.setValue(self.cv(0))
        self.ui.LNAddressSpinBox1.valueChanged.connect(self.lnaddressChanged)
        self.ui.LNAddressSpinBox2.valueChanged.connect(self.lnaddressChanged)
        self.ui.LNAddressSpinBox3.valueChanged.connect(self.lnaddressChanged)

        self.ui.ArduinoPinSpinBox1.setValue(self.cv(1))
        self.ui.ArduinoPinSpinBox1.setValue(self.cv(1))
        self.ui.ArduinoPinSpinBox1.valueChanged.connect(self.arduinopinChanged)
        self.ui.ArduinoPinSpinBox2.valueChanged.connect(self.arduinopinChanged)

        self.ui.pos1SpinBox.setValue(self.cv(2))
        self.ui.pos2SpinBox.setValue(self.cv(3))
        self.ui.speedSpinBox.setValue(self.cv(4))

        self.ui.pos1SpinBox.valueChanged.connect(self.pos1Changed)
        self.ui.pos2SpinBox.valueChanged.connect(self.pos2Changed)
        self.ui.speedSpinBox.valueChanged.connect(self.speedChanged)

        self.update_feedback_1(self.cv(7))
        self.update_feedback_2(self.cv(8))

        self.ui.feedback_1_spinBox.valueChanged.connect(self.feedback_1_changed)
        self.ui.feedback_2_spinBox.valueChanged.connect(self.feedback_2_changed)

        self.decoder.dataChanged.connect(self.cvDataChanged)

    def cv(self, p):
        try:
            return int(self.decoder.CVs[self.slot_parameter_to_cv(p)])
        except ValueError:
            return 0

    def cvDataChanged(self, topleft, bottomright):
        cv = self.decoder.row2cv(topleft.row())
        value = self.decoder.data(topleft)

        if cv > 31:
            pinconf = int((cv - 32) / self.cvsPerPin)
            if pinconf != self.index:
                print("Not for me({}), but ({})".format(self.index, self.ui.comboBox_2.currentIndex()))
                if self.ui.comboBox_2.currentIndex() == 0:  # Servo
                    print(" I'm a servo ({} ?= {})".format(pinconf, self.cv(7)))
                    if pinconf == self.cv(7):
                        self.update_feedback_1()
                    elif pinconf == self.cv(8):
                        self.update_feedback_2()
                return
            pincv = (cv - 32) - (pinconf * self.cvsPerPin)
            print("CV: ", cv, " Pin CV: ", pincv, " Value: ", value)
            try:
                value = int(value)
            except ValueError:
                return

            if pincv == 1:
                self.ui.LNAddressSpinBox1.setValue(value)
                self.ui.LNAddressSpinBox2.setValue(value)
                self.ui.LNAddressSpinBox3.setValue(value)
            # if pincv == 0:
                # self.ui.arduinopinSpinBox1.setValue(value)
                # self.ui.arduinopinSpinBox2.setValue(value)
            if pincv == 2:
                self.ui.pos1SpinBox.setValue(value)
                self.ui.ledValue1SpinBox.setValue(value)
            if pincv == 3:
                self.ui.pos2SpinBox.setValue(value)
                self.ui.ledValue2SpinBox.setValue(value)
            if pincv == 4:
                self.ui.speedSpinBox.setValue(value)
                # self.ui.ledEffectComboBox.setValue(value)
            if pincv == 7:
                self.update_feedback_1(value)
            if pincv == 8:
                self.update_feedback_2(value)

    def update_feedback_1(self, value: int = None):
        if value is None:
            value = self.cv(7)
        self.ui.feedback_1_spinBox.setValue(value)
        if value == 0:
            self.ui.feedback_1_label.setText("N/A")
        elif value > self.decoder.CVs[6]:
            self.ui.feedback_1_label.setText("Create")
        else:
            feedback_1_ln_address = self.decoder.CVs[self.slot_parameter_to_cv(1, value)]
            print("Getting pincv 1 of slot {}: {}".format(value, feedback_1_ln_address))
            color = "#ff0000"
            if self.decoder.CVs[9 + value] == 1:
                color = "#00ff00"
            self.ui.feedback_1_label.setText("<span style='color:{}'>{}</span>".format(color, feedback_1_ln_address))

    def update_feedback_2(self, value: int = None):
        if value is None:
            value = self.cv(8)
        self.ui.feedback_2_spinBox.setValue(value)
        if value == 0:
            self.ui.feedback_2_label.setText("N/A")
        elif value > self.decoder.CVs[6]:
            self.ui.feedback_2_label.setText("Create")
        else:
            feedback_2_ln_address = self.decoder.CVs[self.slot_parameter_to_cv(1, value)]
            print("Getting pincv 1 of slot {}: {}".format(value, feedback_2_ln_address))
            color = "#ff0000"
            if self.decoder.CVs[9 + value] == 1:
                color = "#00ff00"
            self.ui.feedback_2_label.setText("<span style='color:{}'>{}</span>".format(color, feedback_2_ln_address))

    def functionChanged(self, index: int = None):
        cv = self.index + 9
        if index is None:
            index = self.function_map[self.decoder.CVs[cv]]

        if index < 0:
            return
        value = index
        if value == 3:
            value = 0
        self.ui.stackedWidget.setCurrentIndex(value)
        self.ui.comboBox_2.setCurrentIndex(index)
        self.ui.comboBox_3.setCurrentIndex(index)
        self.ui.comboBox_4.setCurrentIndex(index)
        if index == 0:
            value = 2  # servo
        elif index == 1:
            value = 3  # output/LED
        elif index == 2:
            value = 1  # input
        elif index == 3:
            value = 102 # PCA Servo
        else:
            return
        self.decoder.write_cv(cv, value)

    def arduinopinChanged(self, value):
        self.ui.ArduinoPinSpinBox1.setValue(value)
        self.ui.ArduinoPinSpinBox2.setValue(value)
        self.decoder.write_cv(self.slot_parameter_to_cv(0), value)

    def lnaddressChanged(self, value):
        self.decoder.write_cv(self.slot_parameter_to_cv(1), value)

    def pos1Changed(self, value):
        self.decoder.write_cv(self.slot_parameter_to_cv(2), value)

    def pos2Changed(self, value):
        self.decoder.write_cv(self.slot_parameter_to_cv(3), value)

    def speedChanged(self, value):
        self.decoder.write_cv(self.slot_parameter_to_cv(4), value)

    def feedback_1_changed(self, value):
        self.decoder.write_cv(self.slot_parameter_to_cv(7), value)

    def feedback_2_changed(self, value):
        self.decoder.write_cv(self.slot_parameter_to_cv(8), value)

class Dec10001Controller(object):
    """docstring for dec10001controller"""

    def __init__(self, decoder, tabwidget):
        super(Dec10001Controller, self).__init__()
        self.decoder = decoder
        self.tabwidget = tabwidget

        self.generalwidget = QtWidgets.QWidget()

        plugin_directory = os.path.dirname(os.path.abspath(__file__))
        self.ui = QtCompat.loadUi(os.path.join(plugin_directory, "dec10001-1.ui"))

        self.tabs = []
        self.tabs.append(self.tabwidget.addTab(self.ui, "Dec 10001"))
        self.pin_widgets = []

        address = self.decoder.get_cv(1)
        if address is None:
            address = 1

        self.ui.addressSpinBox.setRange(1, 255)
        try:
            self.ui.addressSpinBox.setValue(int(address))
        except ValueError:
            pass
        self.ui.addressSpinBox.valueChanged.connect(self.addressChanged)

        confpins = self.decoder.get_cv(6)
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
        self.decoder.write_cv(1, value)

    @classmethod
    def generalCVs(cls):
        return range(1, 31)

    def confpinsChanged(self, value):
        """docstring for confpinsChanged"""
        self.decoder.write_cv(6, value)
        while len(self.tabs) < value + 1:
            self.pin_widgets.append(PinConfigWidget(len(self.tabs) - 1, self.decoder))
            self.tabs.append(self.tabwidget.addTab(self.pin_widgets[-1].ui, "Slot {}".format(len(self.tabs) - 1)))
            print(self.tabs)

        if len(self.tabs) > (value + 1):
            self.tabwidget.removeTab(self.tabs[-1])
            self.tabs.remove(self.tabs[-1])

    def close(self):
        for tab in self.tabs[::-1]:
            self.tabwidget.removeTab(tab)
