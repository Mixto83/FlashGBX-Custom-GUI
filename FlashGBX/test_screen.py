import os
import parser
import sys
import traceback

from .pyside import QtCore, QtWidgets, QtGui, QApplication
from .Util import APPNAME, VERSION, VERSION_PEP440


class TestScreen(QtWidgets.QWidget):

    ARGS = None

    def __init__(self, args):
        QtWidgets.QWidget.__init__(self)
        self.title = 'Test'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.ARGS = args

        self.layout = QtWidgets.QGridLayout()
        self.button = QtWidgets.QPushButton("Go to og GUI")
        self.connect(self.button, QtCore.SIGNAL("clicked()"), self.restartAsOriginalGUI)

        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def restartAsOriginalGUI(self):
        gui_args = self.ARGS
        print(sys.argv)
        os.execv(sys.executable, ['python'] + [sys.argv[0]])

    def run(self):
        print("run")
        self.show()
        qt_app.exec()

qt_app = QApplication(sys.argv)
qt_app.setApplicationName(APPNAME)