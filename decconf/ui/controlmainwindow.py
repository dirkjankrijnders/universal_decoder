import configparser
import copy
import logging
import time
import queue

from copy import deepcopy

from Qt import QtCore, QtGui, QtWidgets, QtCompat, __qt_version__, __binding__, __binding_version__
import serial.tools.list_ports
from appdirs import *

from yapsy.PluginManager import PluginManager

from decconf.ui.prefdialog import PreferenceDialog
from decconf.datamodel.decoder import DecoderController, cvController
from decconf.datamodel.CV import CVListModel
from decconf.datamodel.CV import CVDelegate

from dummy_serial import DummySerial

from decconf.protocols.loconet import LocoNet as Ln
from decconf.protocols.loconet import make_LNCV_response, parse_LNCV_message, format_loconet_message, checksum_loconet_buffer

from decconf.interfaces.locobuffer import LocoBuffer


class RecieveThread(QtCore.QThread):
    dataReady = QtCore.Signal(object)

    def __init__(self, q):
        super(RecieveThread, self).__init__()
        self.Queue = q

    def run(self):
        while True:
            data = self.Queue.get()
            # this will add a ref to self.data and avoid the destruction
            self.dataReady.emit(deepcopy(data))


class ControlMainWindow(object):
    def __init__(self):
        # super(ControlMainWindow, self).__init__(parent)
        super(ControlMainWindow, self).__init__()

        self.configfile = os.path.join(user_config_dir("Decconf", "Pythsoft"), 'decconf.ini')
        if not os.path.isdir(user_config_dir("Decconf", "Pythsoft")):
            os.mkdir(user_config_dir("Decconf", "Pythsoft"))
        self.config = configparser.ConfigParser()
        self.config['general'] = {}
        self.config['general']['autodetect'] = 'False'
        self.config['general']['autoconnect'] = 'False'
        self.config['general']['device'] = 'None'
        self.config.read(self.configfile)

        self.logger = logging.getLogger('decconf')
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

        self.logger = logging.getLogger('decconf.gui')
        self.logger.info('LNCV Access Gui version 1.0.')

        self.serial = serial.Serial(None, 57600)
        self.lb = None
        self.connected = False

        self.recvQueue = queue.Queue()
        self.sendQueue = queue.Queue()
        self.recvThread = RecieveThread(self.recvQueue)
        self.recvThread.dataReady.connect(self.recieve_loconet_packet, QtCore.Qt.QueuedConnection)
        self.recvThread.start()
        self._prefdialog = None
        self.ui = QtCompat.loadUi("decconf/ui/mainwindow.ui")

        self.ui.show()
        self.setup_menu()
        self.ui.connectserial.setText("Connect")
        self.ui.powerControl.setCheckable(True)
        self.ui.toolBar.addWidget(self.ui.comboBox)
        self.ui.toolBar.addWidget(self.ui.connectserial)
        empty = QtWidgets.QWidget()
        empty.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.ui.toolBar.addWidget(empty)
        self.ui.toolBar.addWidget(self.ui.infoButton)
        self.ui.toolBar.addWidget(self.ui.powerControl)

        self.manager = PluginManager()  # categories_filter={ "Modules": CVDelegate})
        self.classDelegateMapping = dict()
        self.init_module_delegates()

        port_found = False
        for ii, port in enumerate(serial.tools.list_ports.comports()):
            self.ui.comboBox.addItem("{}".format(port[0]), userData=port)

        self.ui.comboBox.addItem("Dummy", userData='dummy')

        port_index = self.ui.comboBox.findText(self.config.get('general', 'device'))
        if port_index >= 0:
            self.ui.comboBox.setCurrentIndex(port_index)
            port_found = True

        self.ui.connectserial.clicked.connect(self.connectserial)
        self.ui.powerControl.clicked.connect(self.powercontrol)
        self.ui.infoButton.clicked.connect(self.infodialog)
        self.ui.DetectButton.clicked.connect(self.detect_modules)

        self.cvController = cvController(self.ui.cvTable)
        self.decodercont = DecoderController(self.ui.treeWidget, self.cvController, self.ui.tabWidget)

        if port_found and self.config.getboolean('general', 'autoconnect'):
            self.connectserial()

        if self.connected and self.config.getboolean('general', 'autodetect'):
            self.detect_modules()

    def connectserial(self):
        # self.decodercont.addDecoder(Decoder(10001, 126, self.lb));
        # self.recvQueue.put(bytes.fromhex('ED0F0105002150112700007F000021'));
        if self.ui.connectserial.text() == "Connect":
            port = self.ui.comboBox.currentText()
            print("Connecting!", port)
            # self.logger.info("Connecting!", port)
            if port == 'Dummy':
                self.serial = DummySerial()
                self.ui.connectserial.setText("Disconnect")
                self.lb = LocoBuffer(self.serial, self.sendQueue, self.recvQueue)
                self.connected = True
                return

            self.serial.port = port
            try:
                self.serial.open()
            except Exception as e:
                self.logger.warning("Failed to open serial port: ", e)
                return

            self.ui.connectserial.setText("Disconnect")
            self.lb = LocoBuffer(self.serial, self.sendQueue, self.recvQueue)
            self.connected = True
        else:
            self.lb = None
            self.connected = False
            self.serial.close()
            self.ui.connectserial.setText("Connect")

    def powercontrol(self):
        if self.lb is not None:
            if self.ui.powerControl.isChecked():
                self.lb.write(checksum_loconet_buffer([Ln.OPC_GPON, 0x00]))
            else:
                self.lb.write(checksum_loconet_buffer([Ln.OPC_GPOFF, 0x00]))

    def infodialog(self):
        if self.lb is not None:
            dec = self.decodercont.selectedDecoder()
            if dec is None:
                return
            dec.readCV(1018)  # Temperature
            dec.readCV(1019)  # UID bytes 0-1
            dec.readCV(1020)  # UID bytes 2-3
            dec.readCV(1021)  # UID bytes 4-5
            dec.readCV(1022)  # UID bytes 6-7
            dec.readCV(1023)  # Version
            dec.readCV(1024)  # FreeRAM
            dec.readCV(1028)  # RxPackets
            dec.readCV(1029)  # RxErrors
            dec.readCV(1030)  # TxPackets
            dec.readCV(1031)  # TxErrors
            dec.readCV(1032)  # Collisions

            from decconf.datamodel.CV import CVListModel

            # infoDialog = QtGui.QDialog(self)
            info_ui = QtCompat.loadUi("decconf/ui/infodialog.ui")
            # infoUi.setupUi(infoDialog);
            infofilter = QtCore.QSortFilterProxyModel()
            infofilter.setFilterRole(QtCore.Qt.UserRole)
            infofilter.setFilterRegExp("info")
            infofilter.setSourceModel(dec)
            info_ui.tableView.setModel(infofilter)
            info_ui.exec()

    def detect_modules(self):
        if self.lb is not None:
            buf = make_LNCV_response(0xFFFF, 0, 0xFFFF, 0, opc=Ln.OPC_IMM_PACKET, src=Ln.LNCV_SRC_KPU,
                                     req=Ln.LNCV_REQID_CFGREQUEST)
            self.lb.write(buf)

    def parse_loconet_packet(self, data):
        pkt = parse_LNCV_message(data)
        if pkt is not None and pkt['SRC'] == Ln.LNCV_SRC_MODULE:
            print("parsed: ", " ".join("{:02x}".format(b) for b in data).upper())
            print("Flags: ", pkt['flags'])
            print(pkt)
            if pkt['SRC'] == Ln.LNCV_SRC_MODULE and pkt['ReqId'] == Ln.LNCV_REQID_CFGREAD:
                if pkt['lncvNumber'] == 0:
                    if pkt['flags'] == 0:
                        print(self.classDelegateMapping.keys())
                        if str(pkt['deviceClass']) in self.classDelegateMapping.keys():
                            dd = copy.copy(self.classDelegateMapping[str(pkt['deviceClass'])])
                        else:
                            dd = CVDelegate()
                        self.decodercont.addDecoder(
                            CVListModel(pkt['deviceClass'], pkt['lncvValue'], cs=self.lb, descriptionDelegate=dd))
                    else:
                        self.logger.debug("ACK on Programming")
                        self.decodercont.selectedDecoder().programmingAck(pkt)
                else:
                    self.decodercont.selectedDecoder().setCV(pkt['lncvNumber'], pkt['lncvValue'])
            print("Found device class: {} module address: {}".format(pkt['deviceClass'], pkt['lncvValue']))

    def recieve_loconet_packet(self, data):
        self.parse_loconet_packet(data)
        _bytes, info = format_loconet_message(data)
        self.ui.ReceivedPacketsList.addItem(_bytes + "\t" + info)

    def _about(self):
        about_msg_box = QtWidgets.QMessageBox()
        about_msg_box.setText("Decoder configurator Loconet CV based decoders")
        about_msg_box.setInformativeText(
            "Qt Version: {}\n"
            "Binding used: {} {}".format(__qt_version__, __binding__, __binding_version__))
        about_msg_box.exec()

    def _export(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self.ui, "Export Data File", "", "CSV data files (*.csv)")
        if filename:
            print("File to export to: {}".format(filename))
            with open(filename[0], 'wt') as fid:
                self.decodercont.selectedDecoder().writeCSV(fid)

    def _quit(self):
        try:
            self.decodercont.selectedDecoder().close()
        except Exception as e:
            pass

        time.sleep(2)
        self.lb = None
        self.connected = False
        self.serial.close()
        exit(0)

    def _pref(self):
        if self._prefdialog is None:
            self._prefdialog = PreferenceDialog(self.config)
        if self._prefdialog.ui.exec():
            with open(self.configfile, 'w') as fid:
                self.config.write(fid)
        else:
            self.config = configparser.ConfigParser()
            self.config.read(self.configfile)

    def setup_menu(self):
        _menuBar = self.ui.menuBar()

        _helpMenu = _menuBar.addMenu("Help")
        _fileMenu = _menuBar.addMenu("File")
        _prefAction = QtWidgets.QAction("Preferences", self.ui, statusTip="Preferences", triggered=self._pref)
        _aboutAction = QtWidgets.QAction("About", self.ui, statusTip="About", triggered=self._about)
        _exportAction = QtWidgets.QAction("Export", self.ui, statusTip="Export", triggered=self._export)
        _quitAction = QtWidgets.QAction("Quit", self.ui, statusTip="Quit", triggered=self._quit)
        _fileMenu.addAction(_exportAction)
        _helpMenu.addAction(_aboutAction)
        _helpMenu.addAction(_prefAction)
        _helpMenu.addAction(_quitAction)

        print("Added menu")

    def init_module_delegates(self):
        self.manager.setPluginPlaces(['decoders'])

        # Load plugins
        self.manager.locatePlugins()
        self.manager.loadPlugins()
        # Activate all loaded plugins
        for pluginInfo in self.manager.getAllPlugins():
            self.manager.activatePluginByName(pluginInfo.name)
            self.classDelegateMapping[str(pluginInfo.details.get('Decoder', 'Class'))] = pluginInfo.plugin_object

        for plugin in self.manager.getAllPlugins():
            self.logger.info("Loaded plugin: {} - {}".format(plugin.details.get('Decoder', 'Class'), plugin.name))
