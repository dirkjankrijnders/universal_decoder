from PySide import QtCore, QtGui
import serial.tools.list_ports

from decconf.ui.preferences import Ui_Dialog 

class PreferenceDialog(QtGui.QDialog):
	"""docstring for PreferenceDialog"""
	def __init__(self, config):
		super(PreferenceDialog, self).__init__()
		self.config = config
		self.ui = Ui_Dialog()
		self.ui.setupUi(self);
		self.applyConfig();
		
		self.ui.deviceCombo.addItem("{}".format("None"), userdata = None);
		for ii, port in enumerate(serial.tools.list_ports.comports()):
			self.ui.deviceCombo.addItem("{}".format(port[0]), userdata = port);
		self.ui.deviceCombo.addItem("{}".format("Dummy"), userdata = 'dummy');
		
		portIndex = self.ui.deviceCombo.findText(self.config.get('general', 'device'))
		print("Found port index ", portIndex)
		if portIndex >=0:
			self.ui.deviceCombo.setCurrentIndex(portIndex);
		self.ui.detectCheckBox.stateChanged.connect(self.detectChanged)
		self.ui.connectCheckBox.stateChanged.connect(self.connectChanged)
		self.ui.deviceCombo.currentIndexChanged.connect(self.deviceChanged)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
	
	def applyConfig(self):
		if self.config.getboolean("general", "autodetect"):
			self.ui.detectCheckBox.setCheckState(QtCore.Qt.Checked)
		else:
			self.ui.detectCheckBox.setCheckState(QtCore.Qt.Unchecked)
		
		if self.config.getboolean("general", "autoconnect"):
			self.ui.connectCheckBox.setCheckState(QtCore.Qt.Checked)
		else:
			self.ui.connectCheckBox.setCheckState(QtCore.Qt.Unchecked)
	
	def detectChanged(self):
		if self.ui.detectCheckBox.checkState() == QtCore.Qt.Checked:
			self.config.set("general", "autodetect", 'True');
		else:
			self.config.set("general", "autodetect", 'False');

	def connectChanged(self):
		if self.ui.connectCheckBox.checkState() == QtCore.Qt.Checked:
			self.config.set("general", "autoconnect", 'True');
		else:
			self.config.set("general", "autoconnect", 'False');

	def deviceChanged(self):
		port = self.ui.deviceCombo.currentText();
		
		if port == "None":
			self.config.set("general", "device", "")
		else:
			self.config.set("general", "device", port)