from PySide import QtCore, QtGui

from .dec100011 import Ui_Form
from .dec100012 import Ui_Form as Ui_Form2

"""class PinConfigWidget(QtGui.QWidget):
	def __init__(self, index, decoder):
		super(PinConfigWidget, self).__init__()
		self.decoder = decoder
		self.index = index
		
		self.currentFunctionWidgets = []
		
		self.verticallayout = QtGui.QVBoxLayout(self);
		
		self.formlayout = QtGui.QFormLayout();
		self.formlayout.setContentsMargins(0, 0, 0, 0);
		self.formlayout.setObjectName("PinFormLayout");
		self.verticallayout.addLayout(self.formlayout);
		
		self.stackedlayout = QtGui.QStackedLayout();
		self.stackedlayout.setObjectName("StackedPinForms")
		self.verticallayout.addLayout(self.stackedlayout);
		
		self.functionlabel = QtGui.QLabel(self);
		self.functionlabel.setObjectName("FunctionLabel");
		self.functionlabel.setText("Pin function");
		self.formlayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.functionlabel)
		
		self.functioncombo = QtGui.QComboBox(self);
		self.functioncombo.setObjectName("FunctionCombo")
		self.formlayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.functioncombo)
		
		self.functioncombo.addItem("None")
		self.functioncombo.addItem("Servo")
		self.functioncombo.addItem("Sensor")
		self.functioncombo.addItem("LED")
		
		self.functioncombo.currentIndexChanged.connect(self.functionChanged);
		
		self.arduinopinlabel = QtGui.QLabel(self);
		self.arduinopinlabel.setObjectName("ArduinoPinLabel");
		self.arduinopinlabel.setText("Arduino pin");
		self.formlayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.arduinopinlabel)
		
		self.arduinopinSpinBox = QtGui.QSpinBox(self);
		self.arduinopinSpinBox.setObjectName("ArduinoPinSpinBox")
		self.formlayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.arduinopinSpinBox);
		
		self.arduinopinSpinBox.valueChanged.connect(self.arduinopinChanged);
		
		self.lnaddresslabel = QtGui.QLabel(self);
		self.lnaddresslabel.setObjectName("LNAddresslabel");
		self.lnaddresslabel.setText("LN Address");
		self.formlayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.lnaddresslabel)
		
		self.lnaddressSpinBox = QtGui.QSpinBox(self);
		self.lnaddressSpinBox.setObjectName("LNAddressSpinBox")
		self.formlayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.lnaddressSpinBox);
		
		self.lnaddressSpinBox.valueChanged.connect(self.lnaddressChanged);
		
		self.stackedlayout.addWidget(self.setupNoneLayout());
		self.stackedlayout.addWidget(self.setupServoLayout());
"""		
class PinConfigWidget(QtGui.QWidget):
	cvsPerPin = 7;
	
	def __init__(self, index, decoder):
		super(PinConfigWidget, self).__init__()
		self.decoder = decoder
		self.index = index
		
		self.ui = Ui_Form2();
		self.ui.setupUi(self);
		
		for i in ["Servo", "LED"]:
			self.ui.comboBox_3.addItem(i);
			self.ui.comboBox_2.addItem(i);
		
		self.ui.comboBox_2.currentIndexChanged.connect(self.functionChanged)
		self.ui.comboBox_3.currentIndexChanged.connect(self.functionChanged)
		
		self.ui.LNAddressSpinBox1.valueChanged.connect(self.lnaddressChanged);
		self.ui.LNAddressSpinBox2.valueChanged.connect(self.lnaddressChanged);

		self.ui.ArduinoPinSpinBox1.valueChanged.connect(self.arduinopinChanged);
		self.ui.ArduinoPinSpinBox2.valueChanged.connect(self.arduinopinChanged);
		
		self.ui.pos1SpinBox.valueChanged.connect(self.pos1Changed);
		self.ui.pos2SpinBox.valueChanged.connect(self.pos2Changed);
		self.ui.speedSpinBox.valueChanged.connect(self.speedChanged);
		
		self.decoder.dataChanged.connect(self.cvDataChanged);
		
	def cvDataChanged(self, topleft, bottomright):
		cv = self.decoder.row2cv(topleft.row());
		value = self.decoder.data(topleft);
		
		if cv > 31:
			pinconf = int((cv -32)/self.cvsPerPin);
			pincv = (cv - 32) - (pinconf * self.cvsPerPin);
			print("CV: ", cv, " Pin CV: ", pincv, " Value: ", value)
			if pincv == 1:
				self.ui.LNAddressSpinBox1.setValue(value);
				self.ui.LNAddressSpinBox2.setValue(value);
			if pincv == 0:
				self.ui.arduinopinSpinBox1.setValue(value);
				self.ui.arduinopinSpinBox2.setValue(value);
			if pincv == 2:
				self.ui.pos1SpinBox.setValue(value);
				self.ui.ledValue1SpinBox.setValue(value);
			if pincv == 3:
				self.ui.pos2SpinBox.setValue(value);
				self.ui.ledValue2SpinBox.setValue(value);
			if pincv == 4:
				self.ui.speedSpinBox.setValue(value);
				self.ui.ledEffectComboBox.setValue(value);
			
	def functionChanged(self, index):
		cv = self.index + 9;
		value = index
		self.ui.stackedWidget.setCurrentIndex(value);
		self.ui.comboBox_2.setCurrentIndex(value);
		self.ui.comboBox_3.setCurrentIndex(value);
		if index == 0:
			value = 2;
		self.decoder.writeCV(cv, value);

	def arduinopinChanged(self, index):
		cv = (self.index - 1) * 8  + 32;
		value = index
		self.ui.ArduinoPinSpinBox1.setValue(value);
		self.ui.ArduinoPinSpinBox2.setValue(value);
		self.decoder.writeCV(cv, value);

	def lnaddressChanged(self, index):
		cv = (self.index - 1) * 8  + 33;
		value = index
		self.decoder.writeCV(cv, value);

	def pos1Changed(self, index):
		cv = (self.index - 1) * 8  + 34;
		value = index
		self.decoder.writeCV(cv, value);

	def pos2Changed(self, index):
		cv = (self.index - 1) * 8  + 35;
		value = index
		self.decoder.writeCV(cv, value);

	def speedChanged(self, index):
		cv = (self.index - 1) * 8  + 36;
		value = index
		self.decoder.writeCV(cv, value);
	
	def setupNoneLayout(self):
		NoneLayout = QtGui.QWidget();
		NoneLayout.formlayout = QtGui.QFormLayout(NoneLayout);
		NoneLayout.formlayout.setContentsMargins(0, 0, 0, 0);
		NoneLayout.formlayout.setObjectName("NoneLayout");

	def setupServoLayout(self):
		ServoLayout = QtGui.QWidget();
		ServoLayout.formlayout = QtGui.QFormLayout(ServoLayout);
		ServoLayout.formlayout.setContentsMargins(0, 0, 0, 0);
		ServoLayout.formlayout.setObjectName("ServoLayout");
		
		ServoLayout.pos1label = QtGui.QLabel(ServoLayout);
		ServoLayout.pos1label.setObjectName("Pos1label");
		ServoLayout.pos1label.setText("Servo Pos 1");
		ServoLayout.formlayout.setWidget(3, QtGui.QFormLayout.LabelRole, ServoLayout.pos1label)
    	
		ServoLayout.pos1SpinBox = QtGui.QSpinBox(ServoLayout);
		ServoLayout.pos1SpinBox.setObjectName("Pos1SpinBox")
		ServoLayout.formlayout.setWidget(3, QtGui.QFormLayout.FieldRole, ServoLayout.pos1SpinBox);
		ServoLayout.pos1SpinBox.valueChanged.connect(self.pos1Changed);
    	
		ServoLayout.pos2label = QtGui.QLabel(ServoLayout);
		ServoLayout.pos2label.setObjectName("Pos2label");
		ServoLayout.pos2label.setText("Servo Pos 2");
		ServoLayout.formlayout.setWidget(4, QtGui.QFormLayout.LabelRole, ServoLayout.pos2label)
    	
		ServoLayout.pos2SpinBox = QtGui.QSpinBox(ServoLayout);
		ServoLayout.pos2SpinBox.setObjectName("Pos2SpinBox")
		ServoLayout.formlayout.setWidget(4, QtGui.QFormLayout.FieldRole, ServoLayout.pos2SpinBox);
		ServoLayout.pos2SpinBox.valueChanged.connect(self.pos2Changed);
    	
		
		#ServoLayout.currentFunctionWidgets.append(ServoLayout.pos1label);
		#ServoLayout.currentFunctionWidgets.append(ServoLayout.pos1SpinBox);
		#ServoLayout.currentFunctionWidgets.append(ServoLayout.pos2label);
		#ServoLayout.currentFunctionWidgets.append(ServoLayout.pos2SpinBox);
		
		return ServoLayout
	
	def addFunctionWidgets(self, function):
		#if function == 1:
		pass
class dec10001controller(object):
	"""docstring for dec10001controller"""
	def __init__(self, decoder, tabwidget):
		super(dec10001controller, self).__init__()
		self.decoder = decoder
		self.tabwidget = tabwidget
		
		self.generalwidget = QtGui.QWidget();
		self.ui = Ui_Form()
		self.ui.setupUi(self.generalwidget);
		
		self.tabs = []
		self.tabs.append(self.tabwidget.addTab(self.generalwidget, "Dec 10001"));

		address = self.decoder.getCV(1);
		if address is None:
			address = 1;
		
		self.ui.addressSpinBox.setRange(1, 255);
		self.ui.addressSpinBox.setValue(address);
		self.ui.addressSpinBox.valueChanged.connect(self.addressChanged);

		confpins = self.decoder.getCV(6);
		if confpins is None:
			confpins = 0;
		
		for slot in range(confpins):
			self.tabs.append(self.tabwidget.addTab(PinConfigWidget(slot, self.decoder), "Slot {}".format(slot)));
		
		self.ui.pinsSpinBox.lineEdit().setReadOnly(True);
		self.ui.pinsSpinBox.setValue(confpins);
		self.ui.pinsSpinBox.valueChanged.connect(self.confpinsChanged);
		self.decoder.parent.dataChanged.connect(self.cvChange)
	
	
	def cvChange(self, cv, value):
		#cv = #self.decoder.row2cv(topleft.row());
		#value = self.decoder.data(topleft);
		if value is None:
			return
		if cv == 1:
			self.ui.addressSpinBox.setValue(int(value));
		elif cv == 6:
			self.ui.pinsSpinBox.setValue(int(value));
	
	def addressChanged(self, value):
		"""docstring for addressChanged"""
		self.decoder.parent.writeCV(1, value);
		
	def generalCVs(self):
		return range(1,31);
		
	def confpinsChanged(self, value):
		"""docstring for confpinsChanged"""
		self.decoder.writeCV(6, value);
		if len(self.tabs) < value +1:
			self.tabs.append(self.tabwidget.addTab(PinConfigWidget(value, self.decoder), "Slot {}".format(value)));
		
		if len(self.tabs) > (value + 1):
			self.tabwidget.removeTab(self.tabs[-1]);
			self.tabs.remove(self.tabs[-1]);
				
		print(self.tabs)
		print(value)