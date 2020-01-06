# -*- coding: utf-8 -*-

# PDF Parser application
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!
#
# Application author: Hoang Quoc Thinh (https://github.com/c0ldf1recsgo)

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
import main


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setGeometry(400, 200, 486, 282)
        MainWindow.setFixedSize(MainWindow.size())
        MainWindow.setAutoFillBackground(False)
        MainWindow.setDocumentMode(False)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(380, 40, 91, 30))
        self.pushButton.setObjectName("pushButton")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(70, 180, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(110, 40, 261, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit.setFont(font)
        self.lineEdit.setMouseTracking(True)
        self.lineEdit.setText("")
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setClearButtonEnabled(False)
        self.lineEdit.setObjectName("lineEdit")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 44, 65, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(12, 100, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")

        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(110, 100, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")

        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(321, 234, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setText("Click here for help")
        self.label_5.adjustSize()
        self.label_5.setObjectName("label_5")

        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(385, 130, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_6.setFont(font)
        self.label_6.setText("")
        self.label_6.adjustSize()
        self.label_6.setObjectName("label_6")

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(380, 94, 91, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(450, 230, 30, 30))
        self.pushButton_3.setObjectName("helpButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 486, 31))
        self.menubar.setDefaultUp(False)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setAutoFillBackground(False)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton.clicked.connect(self.selectFile)
        self.pushButton_2.clicked.connect(self.convert)
        self.pushButton_3.clicked.connect(self.msg_help)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PDF Parser"))
        self.pushButton.setText(_translate("MainWindow", "Browse..."))
        self.label.setText(_translate("MainWindow", "Hello !!! Welcome to PDF convert tool"))
        self.label_2.setText(_translate("MainWindow", "File path:"))
        self.label_3.setText(_translate("MainWindow", "File name:"))
        self.label_4.setText(_translate("MainWindow", "[Empty]"))
        self.pushButton_2.setText(_translate("MainWindow", "Convert"))
        self.pushButton_3.setText(_translate("MainWindow", "?"))
        self.label.adjustSize()

    def selectFile(self):
        self.label_6.setText("")
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None)
        self.lineEdit.setText(fileName)
        self.label_4.setText(os.path.basename(fileName))
        self.label_4.adjustSize()

    def convert(self):
        self.pushButton_2.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.label_6.setText("Please wait...")
        self.label_6.adjustSize()
        fileName = self.lineEdit.text()
        fileExtension = fileName.split(".")[-1]
        if self.label_4.text() == "":
            self.err_noFile()
            self.pushButton_2.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.label_6.setText("")
            pass
        elif fileExtension != "pdf" and fileExtension !="PDF":
            self.err_nonPDF()
            self.lineEdit.clear()
            self.label_4.setText("[Empty]")
            self.pushButton_2.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.label_6.setText("")
            pass
        elif fileExtension == "pdf" or fileExtension =="PDF":
            main.convertPDF(fileName)
            self.msg_success()
            self.pushButton_2.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.label_6.setText("Finished")
            self.label_6.adjustSize()
            pass
        else:
            self.pushButton_2.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.label_6.setText("")
            pass

    def err_noFile(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText("No file to convert !!!\nPlease select a PDF file.")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.exec_()

    def err_nonPDF(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Cannot convert non-PDF file.\nPlease select again.")
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.exec_()

    def msg_success(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Success")
        msg.setText(
        """PDF File has been converted to TXT
and HTML successfully.

Please go to where you stored your PDF file to check."""
        )
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.exec_()

    def msg_help(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Help")
        msg.setText(
        """1. Browse your PDF file, make sure the file is PDF format.
2. Click Convert Button to convert the PDF file then wait a few seconds.
3. Go to the folder contains the PDF file above to see
HTML and TXT file.

Thanks for using !!!"""
        )
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
