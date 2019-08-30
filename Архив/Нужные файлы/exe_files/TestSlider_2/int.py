# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'int.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(702, 719)
        MainWindow.setWindowOpacity(2.0)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(70, 320, 141, 51))
        self.start.setObjectName("start")
        self.result = QtWidgets.QLCDNumber(self.centralwidget)
        self.result.setEnabled(True)
        self.result.setGeometry(QtCore.QRect(250, 260, 161, 50))
        font = QtGui.QFont()
        font.setFamily("MS PGothic")
        self.result.setFont(font)
        self.result.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.result.setMouseTracking(False)
        self.result.setStatusTip("")
        self.result.setWhatsThis("")
        self.result.setLineWidth(1)
        self.result.setMidLineWidth(1)
        self.result.setSmallDecimalPoint(False)
        self.result.setDigitCount(12)
        self.result.setProperty("value", 0.0)
        self.result.setProperty("intValue", 0)
        self.result.setObjectName("result")
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setEnabled(True)
        self.stop.setGeometry(QtCore.QRect(450, 320, 210, 51))
        self.stop.setObjectName("stop")
        self.text_terminal = QtWidgets.QTextBrowser(self.centralwidget)
        self.text_terminal.setEnabled(True)
        self.text_terminal.setGeometry(QtCore.QRect(230, 510, 201, 80))
        self.text_terminal.setObjectName("text_terminal")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(250, 390, 161, 80))
        self.pushButton.setObjectName("pushButton")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setEnabled(False)
        self.textEdit.setGeometry(QtCore.QRect(188, 0, 321, 240))
        self.textEdit.setObjectName("textEdit")
        self.reload = QtWidgets.QPushButton(self.centralwidget)
        self.reload.setGeometry(QtCore.QRect(480, 510, 161, 80))
        self.reload.setObjectName("reload")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 30, 150, 90))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.current_COM_port = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.current_COM_port.setObjectName("current_COM_port")
        self.verticalLayout.addWidget(self.current_COM_port)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(530, 30, 160, 80))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        self.current_speed_ports = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.current_speed_ports.setObjectName("current_speed_ports")
        self.verticalLayout_2.addWidget(self.current_speed_ports)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 702, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.start.setText(_translate("MainWindow", "Запустить"))
        self.stop.setText(_translate("MainWindow", "Экстренное снижение скорости"))
        self.text_terminal.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Подключиться к порту"))
        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Настройте нужный вам порт из списка портов, к которым подключкено какое-либо устройство. Настройте нужную вам скорость порта, нажмите кнопку &quot;Подключиться к порту&quot;, если она изменится на &quot;Подключено&quot; можете запускать режим, нажав на кнопку &quot;Запустить&quot;.</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Если при запуске у вас не идут данные на ардуино, перезапустите программу и проверьте ту ли скорость вы указали. При нажатии кнопки &quot;Экстренная остановка&quot; дождитесь момента, когда скорость снизится до 0, только потом нажимайте кнопку &quot;Перезагрузка системы&quot;, иначе скорость мгновенно спадет до 0.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>"))
        self.reload.setText(_translate("MainWindow", "Перехагрузка системы"))
        self.label.setText(_translate("MainWindow", "    Выберите COM-Порт"))
        self.current_COM_port.setText(_translate("MainWindow", "COM-Порты"))
        self.label_5.setText(_translate("MainWindow", "      Выберите скорость"))
        self.current_speed_ports.setText(_translate("MainWindow", "Выбор скорости"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

