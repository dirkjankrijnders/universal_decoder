from Qt import QtCore, QtGui, QtWidgets

from decconf.datamodel.CV import CVListModel


class cvController(object):
    """docstring for cvController"""

    def __init__(self, tableView):
        super(cvController, self).__init__()
        self.tableView = tableView
        self.decoder = None
        self.decui = None

    def setDecoder(self, dec, widget):
        if not isinstance(dec, CVListModel):
            return

        if self.decoder is not None:
            self.decoder.close()

        self.decoder = dec
        self.decoder.open()
        self.tableView.setModel(self.decoder)
        self.decoder.hasGui()
        self.decui = dec.controller(widget)

    def readCV(self, cv, value):
        self.decoder.setCV(cv, value)


class DecoderController(object):
    """	"""
    desc = {"10001": "Accesory decoder", "11001": "Lokschuppen specialty", "10002": "Loconet Monitor",
            "10003": "Loconet S88 bridge", "5001": "Arduino LNCV example"}

    def __init__(self, widget, cvController, tabwidget):
        """docstring for __init__"""
        super(DecoderController, self).__init__()

        self.widget = widget
        self._classes = dict()
        self.decoders = list()
        self.cvController = cvController
        self.tabwidget = tabwidget
        # self.plugins = plugins

        self.widget.setColumnCount(2)
        self.widget.setHeaderLabels(['Art Nr', 'Description'])

        for cl in DecoderController.desc.keys():
            self._classes[str(cl)] = (
                QtWidgets.QTreeWidgetItem(self.widget, [str(cl), DecoderController.desc[str(cl)]]), [])

        self.widget.itemSelectionChanged.connect(self.select)

    def addDecoder(self, dec):
        # dec.parent = self.cvController
        self._classes[str(dec._class)][1].append(dec._address)
        treeitem = QtWidgets.QTreeWidgetItem(self._classes[str(dec._class)][0], [str(dec._address), "bla"])
        treeitem.setData(0, QtCore.Qt.UserRole, dec)
        print(self._classes[str(dec._class)][0])
        self.decoders.append(dec)

    def selectedDecoder(self):
        return self.widget.selectedItems()[0].data(0, QtCore.Qt.UserRole)

    # return self.decoders[self.widget.selectedItems()[0]]

    def select(self):
        self.cvController.setDecoder(self.widget.selectedItems()[0].data(0, QtCore.Qt.UserRole), self.tabwidget)
