from logging import getLogger

from Qt import QtCore
from yapsy.IPlugin import IPlugin

from decconf.protocols.loconet import start_module_LNCV_programming, stop_module_LNCV_programming, read_module_LNCV, \
    write_module_LNCV, LNCVReadMessage, parse_LNCV_message, LNCVWriteMessage


class CVDelegate(IPlugin):
    def __init__(self, parent=None):
        super(CVDelegate, self).__init__()
        self.parent = parent

    @staticmethod
    def has_gui():
        return False

    @staticmethod
    def is_editable():
        return True

    def cv_description(self, cv):
        return "CV {}".format(cv)

    def controller(self, decoder, tabwidget):
        return None

    def general_cvs(self):
        return [1, 7, 8]

    def set_cv(self, cv, value):
        pass

    def format_cv(self, cv):
        return self.parent.CVs[cv]

    def close(self):
        pass


class CVListModel(QtCore.QAbstractTableModel):
    """Represents a list of CV's"""
    dataChanged = QtCore.Signal(QtCore.QModelIndex, QtCore.QModelIndex)

    def __init__(self, _class, _address, description_delegate=None, cs=None):
        super(CVListModel, self).__init__()
        if description_delegate is not None:
            self.descriptionDelegate = description_delegate
            self.descriptionDelegate.parent = self
        else:
            self.descriptionDelegate = CVDelegate(self)
        self._class = _class
        self._address = _address
        self.cs = cs
        self.logger = getLogger()

        self.CVs = list()
        for cv in range(1, 1100):
            self.CVs.append('')

        self.header = ["CV", "Description", "Value"]

    @property
    def module_class(self):
        return self._class

    @property
    def address(self):
        return self._address

    def open(self):
        if self.cs is None:
            return None

        self.cs.write(start_module_LNCV_programming(self._class, self._address))

    def close(self):
        if self.cs is None:
            return None

        self.cs.write(stop_module_LNCV_programming(self._class, self._address))
        self.descriptionDelegate.close()

    def programming_ack(self, pkt):
        self.read_all_cv()

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
        desc = self.descriptionDelegate.cv_description(cv)

        values = [cv, desc, self.descriptionDelegate.format_cv(cv)]
        return values[index.column()]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        cv = index.row()
        self.CVs[cv] = value
        if role == QtCore.Qt.EditRole:
            try:
                self.write_cv(int(cv), int(value))
            except:
                self.set_cv(cv, value)

        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        if index.column() == 2:
            if self.descriptionDelegate.is_editable:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            else:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[section]
        return None

    def read_all_cv(self):
        for cv in self.descriptionDelegate.general_cvs():
            self.read_cv(cv)

    def message_confirmed(self, msg, reply):
        self.logger.debug("Message confirmed: ", msg)
        if isinstance(msg, LNCVReadMessage):
            pkt = parse_LNCV_message(bytearray(reply))
            self.set_cv(pkt['lncvNumber'], pkt['lncvValue'])
        if isinstance(msg, LNCVWriteMessage):
            pkt = parse_LNCV_message(bytearray(msg.msg))
            self.set_cv(pkt['lncvNumber'], pkt['lncvValue'])

    def read_cv(self, cv):
        self.cs.add_to_queue(LNCVReadMessage(read_module_LNCV(self._class, cv), self))

    def write_cv(self, cv, value):
        if self.cs is not None and self.get_cv(cv) != value:
            self.cs.add_to_queue(LNCVWriteMessage(write_module_LNCV(self._class, cv, value), self))

    def set_cv(self, cv, value):
        self.CVs[cv] = value
        self.logger.debug("CVs:", self.CVs)
        row = cv
        self.logger.debug("cv: ", cv, "row: ", row)
        if row is not None:
            self.dataChanged.emit(self.createIndex(row, 2), self.createIndex(row, 2))
        self.descriptionDelegate.set_cv(cv, value)

    def get_cv(self, cv):
        self.logger.debug("Accessed decoder CV: ", cv)
        self.logger.debug("returned: ", self.CVs[cv])
        return self.CVs[cv]

    def has_gui(self):
        return self.descriptionDelegate.has_gui()

    def controller(self, widget):
        return self.descriptionDelegate.controller(widget, self)

    @staticmethod
    def row2cv(row):
        return row

    def write_CSV(self, fid):
        import csv
        towrite = []
        for i in range(len(self.CVs)):
            towrite.append([i, self.CVs[i]])
        self.logger.debug(towrite)
        writer = csv.writer(fid)
        writer.writerows(towrite)
