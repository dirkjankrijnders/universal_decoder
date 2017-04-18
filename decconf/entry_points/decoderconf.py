#!/usr/bin/env python3
""" Entry point for Qt QUI """

import sys

from Qt import QtWidgets


from decconf.ui.controlmainwindow import ControlMainWindow

def main():
    """ Nothing but a Qt application starter """
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Decoder Configurator")
    my_gui = ControlMainWindow()
    my_gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
