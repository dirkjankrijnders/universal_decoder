from logging import getLogger

from Qt import QtCore
from Qt.QtWidgets import QTreeWidget, QTreeWidgetItem, QTabWidget, QTableView

from decconf.datamodel.CV import CVListModel


class CVController(object):
    """
    Controller for the module detailed view
    """

    def __init__(self, table_view: QTableView):
        super(CVController, self).__init__()
        self.tableView = table_view
        self.decoder = None
        self.decoder_ui = None

    def set_decoder(self, dec: CVListModel, widget):
        if not isinstance(dec, CVListModel):
            return

        if self.decoder is not None:
            self.decoder.close()

        self.decoder = dec
        self.decoder.open()
        self.tableView.setModel(self.decoder)
        self.decoder.has_gui()
        self.decoder_ui = dec.controller(widget)

    def read_cv(self, cv, value):
        self.decoder.set_cv(cv, value)


class DecoderController(object):
    """
    Controller for the treewidget list all detected modules
    """
    desc = {"10001": "Accessory decoder", "11001": "Lokschuppen specialty", "10002": "Loconet Monitor",
            "10003": "Loconet S88 bridge", "10004": "Train lift",  "5001": "Arduino LNCV example"}

    def __init__(self, widget: QTreeWidget, cv_controller: CVController, tab_widget: QTabWidget):
        """docstring for __init__"""
        super(DecoderController, self).__init__()

        self.widget = widget
        self._classes = dict()
        self.decoders = list()
        self.cvController = cv_controller
        self.tab_widget = tab_widget
        self.logger = getLogger()

        self.widget.setColumnCount(2)
        self.widget.setHeaderLabels(['Art Nr', 'Description'])

        for cl in DecoderController.desc.keys():
            self._classes[str(cl)] = (
                QTreeWidgetItem(self.widget, [str(cl), DecoderController.desc[str(cl)]]), [])

        self.widget.itemSelectionChanged.connect(self.select)

    def add_decoder(self, dec: CVListModel):
        self._classes[str(dec.module_class)][1].append(dec.address)
        tree_item = QTreeWidgetItem(self._classes[str(dec.module_class)][0], [str(dec.address), "bla"])
        tree_item.setData(0, QtCore.Qt.UserRole, dec)
        self.logger.debug(self._classes[str(dec.module_class)][0])
        self.decoders.append(dec)

    def selected_decoder(self):
        return self.widget.selectedItems()[0].data(0, QtCore.Qt.UserRole)

    def select(self):
        self.cvController.set_decoder(self.widget.selectedItems()[0].data(0, QtCore.Qt.UserRole), self.tab_widget)
