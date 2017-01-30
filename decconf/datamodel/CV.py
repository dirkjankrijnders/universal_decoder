from copy import deepcopy
from time import sleep

from PySide import QtCore, QtGui
import numpy as np

from yapsy.IPlugin import IPlugin

from decconf.protocols.loconet import startModuleLNCVProgramming, stopModuleLNCVProgramming, readModuleLNCV, writeModuleLNCV, LNCVReadMessage, parseLNCVmsg, LNCVWriteMessage
from decconf.protocols.loconet import LocoNet as LN

#from decoders.dec10001 import dec10001controller
class infoListModel(QtGui.QSortFilterProxyModel):
	def __init__(self, parent):
		super(infoListModel, self).__init__(parent);
		self.parent = parent;
	
	def rowCount(self, parent):
		return 7;
	
	def columnCount(self, parent):
		return 2;
		
	def mapToSource(self, proxyIndex):
		print(proxyIndex);
		if not proxyIndex.isValid():
			return QtCore.QModelIndex()
		return(proxyIndex);
		
	def index(self, row,  column, parent = QtCore.QModelIndex()):
		print(row)
		print(column)
		print(parent)
		return QtCore.QModelIndex(row, column, self)
		#if row == 1:
		#	return self.createIndex(1019, 0);
		if (parent.isValid()):
		 	sourceParent = mapToSource(parent);
	# QMapIterator<QPersistentModelIndex, QPersistentModelIndex> it(proxySourceParent);
	# while (it.hasNext()) {
	# it.next();
	# if (it.value()  sourceParent && it.key().row()  row &&
	# it.key().column() == column)
	# return it.key();
	# }
	# return QModelIndex();
	# }	
class CVDelegate(IPlugin):
	def __init__(self, parent = None):
		super(CVDelegate, self).__init__();
		self.parent = parent;
		
	def hasGui(self):
		return False;
	
	def isEditable(self):
		return(True);
	
	def cvDescription(self, cv):
		return "CV {}".format(cv)
	def controller(self):
		return None
	
	def generalCVs(self):
		return [1,7,8];
	
	def setCV(self, cv, value):
		pass
	
	def formatCV(self, cv):
		return self.parent.CVs[cv];
		
class CVListModel(QtCore.QAbstractTableModel):
	"""	desc = {"10001": [[1, "Address", 1, 1], [6, "No configured pins", 1, 1], [7, "Manufacturer", 1, 0], [8, "Version", 1, 0], [9, "Pin configuration slot 1",1 ,1], [10, "Pin configuration slot 2",1,1], [32, "peri_conf_1[0]",1 ,1 ], [33, "peri_conf_1[1]", 1, 1]],
			"10002": [[7, "Manufacturer", 1, 0], [8, "Version", 1, 0]],
			"5001": [[7, "Manufacturer", 1, 0], [8, "Version", 1, 0]]}
	"""	
	"""Represents a list of CV's"""
	def __init__(self, _class, _address, descriptionDelegate = None, cs = None):
		super(CVListModel, self).__init__()
		if descriptionDelegate is not None:
			self.descriptionDelegate = descriptionDelegate
			self.descriptionDelegate.parent = self;
		else:
			self.descriptionDelegate = CVDelegate(self);
		self._class = _class
		self._address = _address
		self.cs = cs
		
		self.CVs = list();
#		self.CVs = dict();
#		self.show = [0 for cv in range(1,512)];
		for cv in range(1, 1100):
			self.CVs.append('');

		self.header = ["CV", "Description", "Value"];
		
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
		return len(self.CVs);
		
	def columnCount(self, parent):
		return 3;
	
	def data(self, index, role = QtCore.Qt.DisplayRole):
		if not index.isValid():
			return None
		elif role != QtCore.Qt.DisplayRole:
			return None
		cv = index.row();
		if cv is None:
			return None
		desc = self.descriptionDelegate.cvDescription(cv);
		
		vals = [cv, desc, self.descriptionDelegate.formatCV(cv)]
		return vals[index.column()]
		#cvdesc = deepcopy(self.desc[str(self._class)][index.row()])
		#cvdesc.append(self.CVs[str(cvdesc[0])])
		#return cvdesc[index.column()]
	
	def setData(self, index, value, role = QtCore.Qt.EditRole):
		
		cv = index.row();
		self.CVs[cv] = value
		if role == QtCore.Qt.EditRole:
			try:
				self.writeCV(int(cv), int(value));
			except:
				self.setCV(cv, value);
				
		self.dataChanged.emit(index,index);
		return True
		
	def flags(self, index):
		if index.column() == 2:
			if self.descriptionDelegate.isEditable:
				return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
			else:
				return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
		else:
			return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return self.header[section]
		return None

	def readAllCV(self):
		for cv in self.descriptionDelegate.generalCVs():
			self.readCV(cv);

		#for cv in Decoder.desc[str(self._class)]:
		#	self.readCV(cv[0]);
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
		self.CVs[cv] = value
		print("CVs:", self.CVs);
		row = cv
		print("cv: ", cv, "row: ", row)
		if row is not None:
			self.dataChanged.emit(self.createIndex(row, 2), self.createIndex(row, 2))
		self.descriptionDelegate.setCV(cv, value);
		#self.emit(QtCore.SIGNAL("dataChanged()"));
	
	def getCV(self, cv):
		print("Accessed decoder CV: ", cv)
		print("returned: ", self.CVs[cv])
		return self.CVs[cv]
		
	def hasGui(self):
		return self.descriptionDelegate.hasGui();
	
	def controller(self, tabwidget):
		return self.descriptionDelegate.controller();
		
		
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
