import os
import parser
import sys
import threading
import subprocess
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

        self.goToGUIBtn = QtWidgets.QPushButton("Go to og GUI")
        self.connect(self.goToGUIBtn, QtCore.SIGNAL("clicked()"), self.restartAsOriginalGUI)

        self.openEmuBtn = QtWidgets.QPushButton("Play in BGB")
        self.connect(self.openEmuBtn, QtCore.SIGNAL("clicked()"), self.openEmulator)

        self.layout.addWidget(self.goToGUIBtn)
        self.layout.addWidget(self.openEmuBtn)
        self.setLayout(self.layout)

    def restartAsOriginalGUI(self):
        os.execv(sys.executable, ['python'] + [sys.argv[0]])

    def openEmulator(self):
        t = self.popenWithCallback(["C:\\Users\\admin\\Documents\\bgb\\bgb.exe", "C:\\Users\\admin\\Documents\\crystal clear\\Crystal Clear.gbc"], self.onEmulatorClosed)

    def onEmulatorClosed(self):
        print("Emulator closed")

    def popenWithCallback(self, args, on_exit):
        def runInThread(args, on_exit):
            p = subprocess.Popen(args)
            p.wait()
            on_exit()
        thread = threading.Thread(target=runInThread, args=(args, on_exit))
        thread.start()
        return thread

    def run(self):
        self.show()
        qt_app.exec()

qt_app = QApplication(sys.argv)
qt_app.setApplicationName(APPNAME)