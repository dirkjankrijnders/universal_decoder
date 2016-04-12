from copy import deepcopy
from time import sleep

from PySide import QtCore, QtGui
import numpy as np

from loconet import startModuleLNCVProgramming, stopModuleLNCVProgramming, readModuleLNCV, writeModuleLNCV, LNCVReadMessage, parseLNCVmsg, LNCVWriteMessage
from loconet import LocoNet as LN

from decoders.dec10001 import dec10001controller

class Decoder(QtCore.QAbstractTableModel):
	desc = {"10001": [[1, "Address", 1, 1], [6, "No configured pins", 1, 1], [7, "Manufacturer", 1, 0], [8, "Version", 1, 0], [9, "Pin configuration slot 1",1 ,1], [10, "Pin configuration slot 2",1,1], [32, "peri_conf_1[0]",1 ,1 ], [33, "peri_conf_1[1]", 1, 1]],
			"10002": [[7, "Manufacturer", 1, 0], [8, "Version", 1, 0]],
			"5001": [[7, "Manufacturer", 1, 0], [8, "Version", 1, 0]]}
	
	"""Represents a decoder"""
	def __init__(self, _class, _address, cs = None):
		super(Decoder, self).__init__()
		self._class = _class
		self._address = _address
		self.cs = cs
		
		self.CVs = dict();
		self.show = [0 for cv in range(1,512)];
		for cv in range(1, 512):
			self.CVs[str(cv)] = [None, "CV {} ".format(cv), 1, 1];
		self.CVs['7'][3] = 0; 
		self.CVs['8'][3] = 0; 
		self.header = ["CV", "Description", "Value"];
		self._row2cv = []
		for cv, desc, show, rw in Decoder.desc[str(_class)]:
			self.CVs[str(cv)] = [None, desc, rw, show]; 
			self.show[cv] = show;
			if show:
				self._row2cv.append(cv);
		self.cvrow = np.cumsum(self.show);
		self.rowcv = [i for i in range(1,512)]
		for cv, row in enumerate(self.cvrow):
			#print(row, " => ", cv)
			self.rowcv[cv] = row
		print(self._row2cv)
		
	def open(self):
		if self.cs == None:
			return None
		
		self.cs.write(startModuleLNCVProgramming(self._class, self._address));
		
	def close(self):
		if self.cs == None:
			return None
		
		self.cs.write(stopModuleLNCVProgramming(self._class, self._address));

	def programmingAck(self, pkt):
		self.readAllCV();
			
	def rowCount(self, parent):
		return self.cvrow[-1];
		
	def columnCount(self, parent):
		return 3;
	
	def data(self, index, role = QtCore.Qt.DisplayRole):
		if not index.isValid():
			return None
		elif role != QtCore.Qt.DisplayRole:
			return None
		cv = self.row2cv(index.row());
		if cv is None:
			return None
		vals = [cv, self.CVs[str(cv)][1], self.CVs[str(cv)][0]]
		return vals[index.column()]
		#cvdesc = deepcopy(self.desc[str(self._class)][index.row()])
		#cvdesc.append(self.CVs[str(cvdesc[0])])
		#return cvdesc[index.column()]
	
	def setData(self, index, value, role = QtCore.Qt.EditRole):
		cv = self.row2cv(index.row());
		self.CVs[str(cv)][0] = value
		if role == QtCore.Qt.EditRole:
			try:
				self.writeCV(int(cv), int(value));
			except:
				self.setCV(cv, value);
				
		self.dataChanged.emit(index,index);
		return True
		
	def flags(self, index):
		if index.column() == 2:
			if self.row2cv(index.row()) in [7,8]:
				return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
			else:
				return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
		else:
			return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return self.header[section]
		return None

	def readAllCV(self):
		for cv in Decoder.desc[str(self._class)]:
			self.readCV(cv[0]);
			#sleep(0.1)
			
	def messageConfirmed(self, msg, reply):
		print("Message confirmed: ", msg);
		if isinstance(msg, LNCVReadMessage):
			pkt = parseLNCVmsg(bytearray(reply))
			self.setCV(pkt['lncvNumber'], pkt['lncvValue'])
		if isinstance(msg, LNCVWriteMessage):
			pkt = parseLNCVmsg(bytearray(msg.msg))
			self.setCV(pkt['lncvNumber'], pkt['lncvValue'])			
			
	def readCV(self, cv):
		self.cs.addToQueue(LNCVReadMessage(readModuleLNCV(self._class, self._address, cv), self))

	def writeCV(self, cv, value):
		if self.cs is not None and self.getCV(cv) != value:
			self.cs.addToQueue(LNCVWriteMessage(writeModuleLNCV(self._class, self._address, cv, value), self))
		
	def setCV(self, cv, value):
		self.CVs[str(cv)][0] = value
		print("CVs:", self.CVs);
		row = self.cv2row(cv)
		print("cv: ", cv, "row: ", row)
		self.dataChanged.emit(self.createIndex(row, 2), self.createIndex(row, 2))
		#self.emit(QtCore.SIGNAL("dataChanged()"));
	
	def getCV(self, cv):
		print("Accessed decoder CV: ", cv)
		print("returned: ", self.CVs[str(cv)])
		return self.CVs[str(cv)][0]
		
	def row2cv(self, row):
		
		#cv = self.data(self.createIndex(row, 0));
		return self._row2cv[row]
	
	def cv2row(self, cv):
		if self.show[cv] == 0:
			return None
		return self.cvrow[cv]
		row = None
		k = [int(k) for k in self._row2cv];
		k.sort();
		for ii,_cv in enumerate(k):
			if _cv == cv:
				row = ii
		print("CV ", cv, " maps to row: ", row)
		return row
		
	def hasGui(self):
		if self._class == 10001:
			return True
		
		return False
	
	def controller(self, tabwidget):
		if self._class == 10001:
			return dec10001controller(self, tabwidget);
		
		return None
		
		
class cvController(object):
	"""docstring for cvController"""
	def __init__(self, tableView):
		super(cvController, self).__init__()
		self.tableView = tableView
		self.decoder = None
		
	def setDecoder(self, dec, widget):
		if self.decoder is not None:
			self.decoder.close()
		
		self.decoder = dec;
		self.decoder.open()
		self.tableView.setModel(self.decoder);
		self.decui = dec.controller(widget)
		
	def readCV(self, cv, value):
		self.decoder.setCV(cv, value);
			

class DecoderController(object):
	"""	"""
	desc = {"10001": "Accesory decoder", "11001": "Lokschuppen specialty", "10002": "Loconet Monitor", "5001": "Arduino LNCV example"};
	
	def __init__(self, widget, cvController, tabwidget):
		"""docstring for __init__"""
		super(DecoderController, self).__init__()
		
		self.widget = widget;
		self._classes = dict();
		self.decoders = dict();
		self.cvController = cvController;
		self.tabwidget = tabwidget

		self.widget.setColumnCount(2)
		self.widget.setHeaderLabels(['Art Nr', 'Description']);
		
		for cl in DecoderController.desc.keys():
			self._classes[str(cl)] = (QtGui.QTreeWidgetItem(self.widget, [str(cl), DecoderController.desc[str(cl)]]), []);
			#self.decoders[self._classes[str(cl)][0]] = [];
			
		self.widget.itemSelectionChanged.connect(self.select);
		
	def addDecoder(self, dec):
		self._classes[str(dec._class)][1].append(dec._address);
		treeitem = QtGui.QTreeWidgetItem(self._classes[str(dec._class)][0], [str(dec._address), "bla"])
		print(self._classes[str(dec._class)][0])
		self.decoders[treeitem] = dec;
	
	def selectedDecoder(self):
		return self.decoders[self.widget.selectedItems()[0]]
		
	def select(self):
		self.cvController.setDecoder(self.decoders[self.widget.selectedItems()[0]], self.tabwidget)
		