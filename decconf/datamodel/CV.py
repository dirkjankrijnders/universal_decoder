from copy import deepcopy
from time import sleep

from Qt import QtCore, QtGui

from yapsy.IPlugin import IPlugin

from decconf.protocols.loconet import start_module_LNCV_programming, stop_module_LNCV_programming, read_module_LNCV, \
    write_module_LNCV, LNCVReadMessage, parse_LNCV_message, LNCVWriteMessage


class CVDelegate(IPlugin):
    def __init__(self, parent=None):
        super(CVDelegate, self).__init__()
        self.parent = parent

    def hasGui(self):
        return False

    def isEditable(self):
        return True

    def cvDescription(self, cv):
        return "CV {}".format(cv)

    def controller(self, tabwidget):
        return None

    def generalCVs(self):
        return [1, 7, 8]

    def setCV(self, cv, value):
        pass

    def formatCV(self, cv):
        return self.parent.CVs[cv]

    def close(self):
        pass


class CVListModel(QtCore.QAbstractTableModel):
    """Represents a list of CV's"""

    def __init__(self, _class, _address, descriptionDelegate=None, cs=None):
        super(CVListModel, self).__init__()
        if descriptionDelegate is not None:
            self.descriptionDelegate = descriptionDelegate
            self.descriptionDelegate.parent = self
        else:
            self.descriptionDelegate = CVDelegate(self)
        self._class = _class
        self._address = _address
        self.cs = cs

        self.CVs = list()
        for cv in range(1, 1100):
            self.CVs.append('')

        self.header = ["CV", "Description", "Value"]

    def open(self):
        if self.cs is None:
            return None

        self.cs.write(start_module_LNCV_programming(self._class, self._address))

    def close(self):
        if self.cs is None:
            return None

        self.cs.write(stop_module_LNCV_programming(self._class, self._address))
        self.descriptionDelegate.close()

    def programmingAck(self, pkt):
        self.readAllCV()

    def rowCount(self, parent):
        return len(self.CVs)

    def columnCount(self, parent):
        return 3

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role == QtCore.Qt.UserRole:
            if index.row() in [1018, 1019, 1020, 1021, 1022, 1023, 1024, 1028, 1029, 1030, 1031, 1032]:
                return "info"
            else:
                return "none"
        elif role != QtCore.Qt.DisplayRole:
            return None
        cv = index.row()
        if cv is None:
            return None
        desc = self.descriptionDelegate.cvDescription(cv)

        vals = [cv, desc, self.descriptionDelegate.formatCV(cv)]
        return vals[index.column()]

    # cvdesc = deepcopy(self.desc[str(self._class)][index.row()])
    # cvdesc.append(self.CVs[str(cvdesc[0])])
    # return cvdesc[index.column()]

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        cv = index.row()
        self.CVs[cv] = value
        if role == QtCore.Qt.EditRole:
            try:
                self.writeCV(int(cv), int(value))
            except:
                self.setCV(cv, value)

        self.dataChanged.emit(index, index)
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
            self.readCV(cv)

    def messageConfirmed(self, msg, reply):
        print("Message confirmed: ", msg)
        if isinstance(msg, LNCVReadMessage):
            pkt = parse_LNCV_message(bytearray(reply))
            self.setCV(pkt['lncvNumber'], pkt['lncvValue'])
        if isinstance(msg, LNCVWriteMessage):
            pkt = parse_LNCV_message(bytearray(msg.msg))
            self.setCV(pkt['lncvNumber'], pkt['lncvValue'])

    def readCV(self, cv):
        self.cs.add_to_queue(LNCVReadMessage(read_module_LNCV(self._class, cv), self))

    def writeCV(self, cv, value):
        if self.cs is not None and self.getCV(cv) != value:
            self.cs.add_to_queue(LNCVWriteMessage(write_module_LNCV(self._class, cv, value), self))

    def setCV(self, cv, value):
        self.CVs[cv] = value
        print("CVs:", self.CVs)
        row = cv
        print("cv: ", cv, "row: ", row)
        if row is not None:
            self.dataChanged.emit(self.createIndex(row, 2), self.createIndex(row, 2))
        self.descriptionDelegate.setCV(cv, value)

    # self.emit(QtCore.SIGNAL("dataChanged()"))

    def getCV(self, cv):
        print("Accessed decoder CV: ", cv)
        print("returned: ", self.CVs[cv])
        return self.CVs[cv]

    def hasGui(self):
        return self.descriptionDelegate.hasGui()

    def controller(self, widget):
        return self.descriptionDelegate.controller(widget)

    def row2cv(self, row):
        return row

    def writeCSV(self, fid):
        import csv
        towrite = []
        for i in range(len(self.CVs)):
            # if self.CVs[i]:
            towrite.append([i, self.CVs[i]])
        print(towrite)
        # np.savetxt(fid, towrite, delimiter="")  #, header = "".join(self.header))
        writer = csv.writer(fid)
        writer.writerows(towrite)


class cvController(object):
    """docstring for cvController"""

    def __init__(self, tableView):
        super(cvController, self).__init__()
        self.tableView = tableView
        self.decoder = None
        self.decui = None


def setDecoder(self, dec, widget):
    if self.decoder is not None:
        self.decoder.close()

    self.decoder = dec
    self.decoder.open()
    self.tableView.setModel(self.decoder)
    self.decui = dec.controller(widget)


def readCV(self, cv, value):
    self.decoder.setCV(cv, value)
