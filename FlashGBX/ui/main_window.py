# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                               QProgressBar, QPushButton, QRadioButton, QSizePolicy,
                               QSpacerItem, QSplitter, QStatusBar, QTabWidget,
                               QVBoxLayout, QWidget)


class MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(349, 463)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(0, 0))
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(16)
        font.setBold(False)
        self.tabWidget.setFont(font)
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Triangular)
        self.tabWidget.setIconSize(QSize(16, 16))
        self.play_tab = QWidget()
        self.play_tab.setObjectName(u"play_tab")
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(9)
        font1.setBold(False)
        self.play_tab.setFont(font1)
        self.playButton = QPushButton(self.play_tab)
        self.playButton.setObjectName(u"playButton")
        self.playButton.setGeometry(QRect(90, 150, 131, 71))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI Semibold"])
        font2.setPointSize(14)
        font2.setBold(False)
        self.playButton.setFont(font2)
        self.disconnectButton = QPushButton(self.play_tab)
        self.disconnectButton.setObjectName(u"disconnectButton")
        self.disconnectButton.setGeometry(QRect(260, 380, 75, 24))
        self.progressBar = QProgressBar(self.play_tab)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(70, 330, 171, 23))
        self.progressBar.setValue(24)
        self.stopButton = QPushButton(self.play_tab)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setGeometry(QRect(240, 330, 41, 24))
        self.saveToCartButton = QPushButton(self.play_tab)
        self.saveToCartButton.setObjectName(u"saveToCartButton")
        self.saveToCartButton.setGeometry(QRect(230, 180, 81, 41))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(9)
        font3.setBold(False)
        font3.setKerning(True)
        self.saveToCartButton.setFont(font3)
        self.pushButton = QPushButton(self.play_tab)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(90, 230, 111, 24))
        self.pushButton_2 = QPushButton(self.play_tab)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(90, 260, 91, 24))
        self.pushButton_3 = QPushButton(self.play_tab)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(90, 290, 91, 24))
        self.splitter = QSplitter(self.play_tab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setGeometry(QRect(10, 6, 331, 131))
        self.splitter.setOrientation(Qt.Vertical)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.horizontalLayout_3 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.radioButton = QRadioButton(self.layoutWidget)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setFont(font1)

        self.horizontalLayout_3.addWidget(self.radioButton)

        self.radioButton_2 = QRadioButton(self.layoutWidget)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.horizontalLayout_3.addWidget(self.radioButton_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButton_4 = QPushButton(self.layoutWidget)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.horizontalLayout_3.addWidget(self.pushButton_4)

        self.splitter.addWidget(self.layoutWidget)
        self.horizontalLayoutWidget = QWidget(self.splitter)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayout_4 = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gameLabel = QLabel(self.horizontalLayoutWidget)
        self.gameLabel.setObjectName(u"gameLabel")

        self.verticalLayout.addWidget(self.gameLabel)

        self.romTitleLabel = QLabel(self.horizontalLayoutWidget)
        self.romTitleLabel.setObjectName(u"romTitleLabel")

        self.verticalLayout.addWidget(self.romTitleLabel)

        self.gameCodeLabel = QLabel(self.horizontalLayoutWidget)
        self.gameCodeLabel.setObjectName(u"gameCodeLabel")

        self.verticalLayout.addWidget(self.gameCodeLabel)

        self.bootLabel = QLabel(self.horizontalLayoutWidget)
        self.bootLabel.setObjectName(u"bootLabel")

        self.verticalLayout.addWidget(self.bootLabel)

        self.rtcLabel = QLabel(self.horizontalLayoutWidget)
        self.rtcLabel.setObjectName(u"rtcLabel")

        self.verticalLayout.addWidget(self.rtcLabel)

        self.horizontalLayout_4.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gameText = QLabel(self.horizontalLayoutWidget)
        self.gameText.setObjectName(u"gameText")

        self.verticalLayout_2.addWidget(self.gameText)

        self.romText = QLabel(self.horizontalLayoutWidget)
        self.romText.setObjectName(u"romText")

        self.verticalLayout_2.addWidget(self.romText)

        self.gameCodeText = QLabel(self.horizontalLayoutWidget)
        self.gameCodeText.setObjectName(u"gameCodeText")

        self.verticalLayout_2.addWidget(self.gameCodeText)

        self.bootText = QLabel(self.horizontalLayoutWidget)
        self.bootText.setObjectName(u"bootText")

        self.verticalLayout_2.addWidget(self.bootText)

        self.rtcText = QLabel(self.horizontalLayoutWidget)
        self.rtcText.setObjectName(u"rtcText")

        self.verticalLayout_2.addWidget(self.rtcText)

        self.horizontalLayout_4.addLayout(self.verticalLayout_2)

        self.splitter.addWidget(self.horizontalLayoutWidget)
        self.tabWidget.addTab(self.play_tab, "")
        self.write_tab = QWidget()
        self.write_tab.setObjectName(u"write_tab")
        self.tabWidget.addTab(self.write_tab, "")
        self.settings_tab = QWidget()
        self.settings_tab.setObjectName(u"settings_tab")
        self.settings_tab.setFont(font1)
        self.pushButton_5 = QPushButton(self.settings_tab)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(10, 10, 101, 21))
        self.tabWidget.addTab(self.settings_tab, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.playButton.setText(QCoreApplication.translate("MainWindow", u"PLAY", None))
        self.disconnectButton.setText(QCoreApplication.translate("MainWindow", u"Disconnect", None))
        self.stopButton.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.saveToCartButton.setText(QCoreApplication.translate("MainWindow", u"SAVE \n"
                                                                               "TO CART", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"PLAY ON STADIUM", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"BACKUP ROM", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"BACKUP SAVE", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"GB", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"GBA", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.gameLabel.setText(QCoreApplication.translate("MainWindow", u"Game: ", None))
        self.romTitleLabel.setText(QCoreApplication.translate("MainWindow", u"ROM Title: ", None))
        self.gameCodeLabel.setText(QCoreApplication.translate("MainWindow", u"Game Code and Revision: ", None))
        self.bootLabel.setText(QCoreApplication.translate("MainWindow", u"Boot Logo: ", None))
        self.rtcLabel.setText(QCoreApplication.translate("MainWindow", u"Real Time Clock: ", None))
        self.gameText.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.romText.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.gameCodeText.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.bootText.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.rtcText.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.play_tab),
                                  QCoreApplication.translate("MainWindow", u"PLAY", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.write_tab),
                                  QCoreApplication.translate("MainWindow", u"WRITE", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Go to FlashGBX", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settings_tab),
                                  QCoreApplication.translate("MainWindow", u"SETTINGS", None))
    # retranslateUi
