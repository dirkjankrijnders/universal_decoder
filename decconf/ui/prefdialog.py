import serial.tools.list_ports

from Qt import QtCore, QtCompat


class PreferenceDialog(object):
    """docstring for PreferenceDialog"""

    def __init__(self, config):
        super(PreferenceDialog, self).__init__()
        self.config = config
        self.ui = QtCompat.loadUi("decconf/ui/preferences.ui")
        self.apply_config()

        self.ui.deviceCombo.addItem("{}".format("None"), userData=None)
        for ii, port in enumerate(serial.tools.list_ports.comports()):
            self.ui.deviceCombo.addItem("{}".format(port[0]), userData=port)
        self.ui.deviceCombo.addItem("{}".format("Dummy"), userData='dummy')

        port_index = self.ui.deviceCombo.findText(self.config.get('general', 'device'))
        print("Found port index ", port_index)
        if port_index >= 0:
            self.ui.deviceCombo.setCurrentIndex(port_index)
        self.ui.detectCheckBox.stateChanged.connect(self.detect_changed)
        self.ui.connectCheckBox.stateChanged.connect(self.connect_changed)
        self.ui.deviceCombo.currentIndexChanged.connect(self.device_changed)

    def apply_config(self):
        if self.config.getboolean("general", "autodetect"):
            self.ui.detectCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.detectCheckBox.setCheckState(QtCore.Qt.Unchecked)

        if self.config.getboolean("general", "autoconnect"):
            self.ui.connectCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.connectCheckBox.setCheckState(QtCore.Qt.Unchecked)

    def detect_changed(self):
        if self.ui.detectCheckBox.checkState() == QtCore.Qt.Checked:
            self.config.set("general", "autodetect", 'True')
        else:
            self.config.set("general", "autodetect", 'False')

    def connect_changed(self):
        if self.ui.connectCheckBox.checkState() == QtCore.Qt.Checked:
            self.config.set("general", "autoconnect", 'True')
        else:
            self.config.set("general", "autoconnect", 'False')

    def device_changed(self):
        port = self.ui.deviceCombo.currentText()

        if port == "None":
            self.config.set("general", "device", "")
        else:
            self.config.set("general", "device", port)
