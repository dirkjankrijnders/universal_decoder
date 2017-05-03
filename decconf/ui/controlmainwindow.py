import configparser
import copy
import logging
import os
import time
import queue

from copy import deepcopy

from PySide import QtCore, QtGui
import serial.tools.list_ports
from appdirs import *

from yapsy.PluginManager import PluginManager

from decconf.ui.mainwindow import Ui_MainWindow
from decconf.ui.prefdialog import PreferenceDialog
#from decconf.datamodel.treemodel import TreeModel, TreeItem
from decconf.datamodel.decoder import DecoderController, cvController
from decconf.datamodel.CV import CVListModel
from decconf.datamodel.CV import CVDelegate

from dummy_serial import dummySerial

from decconf.protocols.loconet import LocoNet as LN
from decconf.protocols.loconet import makeLNCVresponse, parseLNCVmsg, formatLNmsg, checksumLnBuf

from decconf.interfaces.locobuffer import LocoBuffer

class RecieveThread(QtCore.QThread):
	dataReady = QtCore.Signal(object)
	
	def __init__(self, q):
		super(RecieveThread, self).__init__();
		self.Queue = q
		
	def run(self):
		while True:
			self.data = self.Queue.get();
      		# this will add a ref to self.data and avoid the destruction 
			self.dataReady.emit(deepcopy(self.data)) 
	  
class ControlMainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(ControlMainWindow, self).__init__(parent)

		self.configfile = os.path.join(user_config_dir("Decconf", "Pythsoft"), 'decconf.ini')
		if not os.path.isdir(user_config_dir("Decconf", "Pythsoft")):
			os.mkdir(user_config_dir("Decconf", "Pythsoft"))
		self.config = configparser.ConfigParser();
		self.config['general'] = {}
		self.config['general']['autodetect'] = 'False'
		self.config['general']['autoconnect'] = 'False'
		self.config['general']['device'] = 'None'
		self.config.read(self.configfile);
		
		self.logger = logging.getLogger('decconf');
		self.logger.setLevel(logging.DEBUG)
		logging.getLogger('yapsy').setLevel(logging.DEBUG)
		# create console handler and set level to debug
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
	
		# create formatter
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
		# add formatter to ch
		ch.setFormatter(formatter)
	
		# add ch to logger
		self.logger.addHandler(ch)
		
		self.logger = logging.getLogger('decconf.gui');
		self.logger.info('LNCV Access Gui version 1.0.');

		self.serial = serial.Serial(None, 57600);
		self.lb = None;
		self.connected = False
		
		self.recvQueue = queue.Queue();
		self.sendQueue = queue.Queue();
		self.recvThread = RecieveThread(self.recvQueue);
		self.recvThread.dataReady.connect(self.recvPkt, QtCore.Qt.QueuedConnection);
		self.recvThread.start()
		self._prefdialog = None
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.SetupMenu();
		self.ui.connectserial.setText("Connect")
		self.ui.powerControl.setCheckable(True);
		self.ui.toolBar.addWidget(self.ui.comboBox);
		self.ui.toolBar.addWidget(self.ui.connectserial);
		empty = QtGui.QWidget();
		empty.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred);
		self.ui.toolBar.addWidget(empty);
		self.ui.toolBar.addWidget(self.ui.infoButton);
		self.ui.toolBar.addWidget(self.ui.powerControl);
		
		self.moduleDelegates = self.initModuleDelegates();
		
		portFound = False
		for ii, port in enumerate(serial.tools.list_ports.comports()):
			self.ui.comboBox.addItem("{}".format(port[0]), userdata = port);
		
		self.ui.comboBox.addItem("Dummy", userdata = 'dummy');
		
		portIndex = self.ui.comboBox.findText(self.config.get('general', 'device'))
		if portIndex >=0:
			self.ui.comboBox.setCurrentIndex(portIndex);
			portFound = True
				
		self.ui.connectserial.clicked.connect(self.connectserial);
		self.ui.powerControl.clicked.connect(self.powercontrol);
		self.ui.infoButton.clicked.connect(self.infodialog);
		self.ui.DetectButton.clicked.connect(self.detectModules);
		
		self.cvController = cvController(self.ui.cvTable)
		self.decodercont = DecoderController(self.ui.treeWidget, self.cvController, self.ui.tabWidget);
		
		if portFound and self.config.getboolean('general', 'autoconnect'):
			self.connectserial();
		
		if self.connected and self.config.getboolean('general', 'autodetect'):
			self.detectModules();
			
	def connectserial(self):
		#self.decodercont.addDecoder(Decoder(10001, 126, self.lb));
		#self.recvQueue.put(bytes.fromhex('ED0F0105002150112700007F000021'));
		if self.ui.connectserial.text() == "Connect":
			port = self.ui.comboBox.currentText();
			print("Connecting!", port)
			#self.logger.info("Connecting!", port)
			if port == 'Dummy':
				self.serial = dummySerial();
				self.ui.connectserial.setText("Disconnect");
				self.lb = LocoBuffer(self.serial, self.sendQueue, self.recvQueue);
				self.connected = True
				return
				
			self.serial.port = port;
			try:
				self.serial.open();
			except Exception as e:
				self.logger.warn("Failed to open serial port: ", e);
				return
		
			self.ui.connectserial.setText("Disconnect");
			self.lb = LocoBuffer(self.serial, self.sendQueue, self.recvQueue);
			self.connected = True
		else:
			self.lb = None;
			self.connected = False
			self.serial.close();
			self.ui.connectserial.setText("Connect")
		
#		self.decodercont.addDecoder(Decoder(10001, 126, self.lb));
		
		
	def powercontrol(self):
		if self.lb is not None:
			if self.ui.powerControl.isChecked():
				self.lb.write(checksumLnBuf([LN.OPC_GPON, 0x00]));
			else:
				self.lb.write(checksumLnBuf([LN.OPC_GPOFF, 0x00]));
	
	def infodialog(self):
		if self.lb is not None:
			dec = self.decodercont.selectedDecoder();
			dec.readCV(1018); # Temperature
			dec.readCV(1019); # UID bytes 0-1
			dec.readCV(1020); # UID bytes 2-3
			dec.readCV(1021); # UID bytes 4-5
			dec.readCV(1022); # UID bytes 6-7
			dec.readCV(1023); # Version
			dec.readCV(1024); # FreeRAM
			dec.readCV(1028); # RxPackets
			dec.readCV(1029); # RxErrors
			dec.readCV(1030); # TxPackets
			dec.readCV(1031); # TxErrors
			dec.readCV(1032); # Collisions
			
			from decconf.ui.infodialog import Ui_Dialog
			from decconf.datamodel.CV import infoListModel
			
			infoDialog = QtGui.QDialog(self)
			infoUi = Ui_Dialog();
			infoUi.setupUi(infoDialog);
			infoUi.tableView.setModel(infoListModel(dec));
			infoDialog.show();
			
	def detectModules(self):
		if self.lb is not None:
			buf = makeLNCVresponse(0xFFFF,0,0xFFFF, 0, opc = LN.OPC_IMM_PACKET, src = LN.LNCV_SRC_KPU, req = LN.LNCV_REQID_CFGREQUEST);
			self.lb.write(buf)
			
	def addClass(self, _class):
		if str(_class) not in self.classes.keys():
			self.classes[str(_class)] = TreeItem([str(_class)], parent = self.moduleModel.rootItem);
			self.moduleModel.addRootItem(self.classes[str(_class)])

	def addModule(self, _class, module):
		_class = str(_class)
		module = str(module)
		item = TreeItem([module], parent = self.classes[_class])
		self.moduleModel.addChildItem(item, parent = self.classes[_class]);
		"""if module not in self.modules.keys():
			self.modules[_class] = [TreeItem([module], parent = self.classes[_class])];
			self.classes[_class].appendChild(self.modules[_class][0])
		else:
			self.modules[_class].append(TreeItem([module], parent = self.classes[_class]));
			self.classes[_class].appendChild(self.modules[_class][-1])
		self.moduleModel.rowsInserted.emit(self, self.moduleModel.rowCount(parent = self.classes[_class]) - 1, self.moduleModel.rowCount(parent = self.classes[_class]) - 1)
		"""
			
	def parseLNPkt(self, data):
		pkt  = parseLNCVmsg(data);
		if pkt is not None and pkt['SRC'] == LN.LNCV_SRC_MODULE:
			print("parsed: ", " ".join("{:02x}".format(b) for b in data).upper())
			print("Flags: ", pkt['flags']);
			print(pkt);
			#self.addClass(pkt['deviceClass']);
			#self.addModule(pkt['deviceClass'], pkt['lncvValue']);
			if pkt['SRC'] == LN.LNCV_SRC_MODULE and pkt['ReqId'] == LN.LNCV_REQID_CFGREAD:
				if pkt['lncvNumber'] == 0:
					if pkt['flags'] == 0:
						print(self.classDelegateMapping.keys());
						if str(pkt['deviceClass']) in self.classDelegateMapping.keys():
							dd = copy.copy(self.classDelegateMapping[str(pkt['deviceClass'])])
						else:
							dd = CVDelegate();
						self.decodercont.addDecoder(CVListModel(pkt['deviceClass'], pkt['lncvValue'], cs = self.lb, descriptionDelegate = dd));
					else:
						self.logger.debug("ACK on Programming")
						self.decodercont.selectedDecoder().programmingAck(pkt);
				else:
					self.decodercont.selectedDecoder().setCV(pkt['lncvNumber'], pkt['lncvValue']);
			print("Found device class: {} module address: {}".format( pkt['deviceClass'], pkt['lncvValue']));
			
	def recvPkt(self,data):
		self.parseLNPkt(data);
		_bytes, info = formatLNmsg(data);
		self.ui.ReceivedPacketsList.addItem(_bytes + "\t" + info);
		print(data)
	
	def _about(self):
		print("About triggered");
		
	def _quit(self):
		try:
			self.decodercont.selectedDecoder().close();
		except:
			pass
		
		time.sleep(2);
		self.lb = None;
		self.connected = False
		self.serial.close();
		exit(0);
		
	def _pref(self):
		if self._prefdialog is None:
			self._prefdialog = PreferenceDialog(self.config);
		if self._prefdialog.exec():
			with open(self.configfile, 'w') as fid:
				self.config.write(fid)
		else:
			self.config = configparser.ConfigParser();
			self.config.read(self.configfile);
		
	def SetupMenu(self):
		self._menuBar = self.menuBar()
		#self._menuBar = QtGui.QMenuBar()
		self._menuBar.setNativeMenuBar(True)
		self.setMenuBar(self._menuBar)
		self._helpMenu = self._menuBar.addMenu("Help")
		self._prefAction = QtGui.QAction("Preferences", self, statusTip="Preferences", triggered=self._pref)
		self._aboutAction = QtGui.QAction("About", self, statusTip="About", triggered=self._about)
		self._quitAction = QtGui.QAction("Quit", self, statusTip="Quit", triggered=self._quit)
		self._helpMenu.addAction(self._aboutAction)
		self._helpMenu.addAction(self._prefAction)
		self._helpMenu.addAction(self._quitAction)
		self._menuBar.show()
		#print("Added menu")
	
	def initModuleDelegates(self):
		self.manager = PluginManager(); #categories_filter={ "Modules": CVDelegate})
		self.manager.setPluginPlaces(['decoders']);
		
		# Load plugins
		self.manager.locatePlugins()
		self.manager.loadPlugins()
		self.classDelegateMapping = dict();
		# Activate all loaded plugins
		for pluginInfo in self.manager.getAllPlugins():
		   self.manager.activatePluginByName(pluginInfo.name)
		   self.classDelegateMapping[str(pluginInfo.details.get('Decoder', 'Class'))] = pluginInfo.plugin_object;

		for plugin in self.manager.getAllPlugins():
			self.logger.info("Loaded plugin: {} - {}".format(plugin.details.get('Decoder', 'Class'), plugin.name));
		