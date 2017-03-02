#!/usr/bin/env python3

import sys

from Qt import QtCore, QtGui, QtWidgets


from decconf.ui.controlmainwindow import ControlMainWindow

def main():
	"""docstring for main"""
	app = QtWidgets.QApplication(sys.argv)
	app.setApplicationName("Decoder Configurator")
	mySW = ControlMainWindow()
	mySW.show()
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	main()