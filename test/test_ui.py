#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
sys.path.append("..")
from scripts.main import UserUI

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    UI = UserUI()
    UI.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
