import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QSlider, QApplication, QVBoxLayout)
from PyQt5 import QtWidgets, QtCore
import sys
import serial
import time
import serial.tools.list_ports
import glob
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton

current_port = ''

current_speed = ''
flag_port = False
flag_speed = False
flag_start = False
flag_stop = True
stop_speed = 0
x = 0
data_in_arduino = 0
print('Loading...')


def Search(__baudrate=115200, timeSleep=5):
    speed_signal = pyqtSignal(bytes)

    __COMlist = []
    __COM = ['COM' + str(i) for i in range(100)]

    for _COM in __COM:
        try:
            COMport = (serial.Serial(port=_COM,
                                     baudrate=__baudrate,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     bytesize=serial.EIGHTBITS,
                                     timeout=0))
            if COMport:
                __COMlist.append(_COM)

        except Exception as e:
            pass
    return __COMlist


def CheckSerialPortMessage(__activeCOM=Search(), __baudrate=115200, __timeSleep=5):
    try:
        for __COM in __activeCOM:

            port = serial.Serial(__COM, __baudrate)
            time.sleep(__timeSleep)
            large = len(port.readline())
            port.read(large)

            while large > 3:
                for a in range(__timeSleep):

                    date = port.readline().decode().split()

                    if 'treadmill' in date:
                        return __COM

    except Exception as e:
        print(e)


CheckSerialPortMessage()


class Window2(QWidget):
    def __init__(self):
        super(Window2, self).__init__()
        self.setWindowTitle('Информация о трекерах')


class SerialThread(QThread):
    def __init__(self):
        global current_speed, current_port
        super().__init__()
        self.speed = 1
        port = serial.Serial(current_port, current_speed)
        self.port = port
        self.rt = None
        self.start()

    def run(self):
        while True:
            self.write_to_port()
            time.sleep(0.1)

    def stop(self):
        if self.rt:
            self.rt.join()

    def write_to_port(self):
        global x, data_in_arduino, flag_stop
        if flag_stop:
            x = str(self.speed) + '.'
        if not flag_stop:
            if self.speed != 0:
                self.speed -= 1
                x = str(self.speed) + '.'
            else:
                x = str(0) + '.'

        self.port.write(bytes(x, 'utf-8'))
        data_in_arduino = x
        print(self.port.readline())


class Sliderdemo(QMainWindow):
    speed_signal = pyqtSignal(bytes)

    def __init__(self):
        super(Sliderdemo, self).__init__()
        uic.loadUi('int.ui', self)
        self.initUI()

    def initUI(self):
        global stop_speed
        self.list_need_trackers = []
        self.head = self.Head.isChecked
        self.L_hand = self.LHand.isChecked
        self.L_leg = self.LLeg.isChecked
        self.R_leg = self.RLeg.isChecked
        self.R_hand = self.Rhand.isChecked
        layout = QVBoxLayout()
        layout.addSpacing(20)
        layout.addWidget(self.head)
        self.radiobox.clicked.connect(self.add_head)
        layout.addSpacing(20)
        layout.addWidget(self.L_hand)
        self.radiobox.clicked.connect(self.add_L_hand)
        layout.addSpacing(20)
        layout.addWidget(self.L_leg)
        self.radiobox.clicked.connect(self.add_L_leg)
        layout.addSpacing(20)
        layout.addWidget(self.R_leg)
        self.radiobox.clicked.connect(self.add_R_leg)
        layout.addSpacing(20)
        layout.addWidget(self.R_hand)
        self.radiobox.clicked.connect(self.add_R_hand)
        self.setLayout(layout)
        self.start.clicked.connect(self.button_start)
        self.current_speed_ports.clicked.connect(self.transform_selection)
        self.get_info_trackers.clicked.connect(self.button_get_info_trackers)
        self.current_COM_port.clicked.connect(self.get_dialog)
        self.pushButton.clicked.connect(self.button_connection)
        self.secondWin = None
        self.stop.clicked.connect(self.button_stop)
        self.setWindowTitle("Window1")
        self.result.display(1)
        self.speed = 0
        self.text_terminal.setText(
            "       Проверка подключения")
        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setGeometry(250, 310, 160, 22)
        self.sld.setMinimum(0)
        self.sld.setTickInterval(1)
        self.sld.setMaximum(255)
        self.sld.setValue(1)
        self.sld.setTickPosition(QSlider.TicksBelow)
        self.sld.setTickInterval(10)
        self.sld.valueChanged[int].connect(self.valuechange)
        self.sld.valueChanged.connect(self.result.display)
        self.sld.setEnabled(False)
        self.get_info_trackers.setEnabled(False)
        vbox = QVBoxLayout()
        vbox.addWidget(self.result)
        vbox.addWidget(self.sld)
        self.show()

    def get_dialog(self):
        global current_port, flag_port
        current_port, flag_port = QInputDialog.getItem(self, "Выберите COM-порт",
                                                       "Доступные COM-Порты",
                                                       Search, 0, False)
        return current_port

    def transform_selection(self):
        global current_speed, flag_speed
        speeds = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
        current_speed, flag_speed = QInputDialog.getItem(self, "Выберите скорость", "Доступные скорости",
                                                         speeds, 0, False)
        return current_speed

    def button_connection(self):
        global current_speed, current_port, flag_speed, flag_port, flag_start
        if flag_speed and flag_port:
            try:
                flag_start = True

                self.pushButton.setText('Подключено')
                self.text_terminal.setText(
                    "Порт, к которому вы подключились: " + current_port +
                    " Скорость порта, которую вы выбрали: " + current_speed)
            except Exception as e:
                self.pushButton.setText(e)
                print(e)
        else:
            if not flag_port and flag_speed:
                self.text_terminal.setText(
                    "Вы не выбрали порт, повторите попытку.")
            if not flag_speed and flag_port:
                self.text_terminal.setText(
                    "Вы не выбрали скорость порта, повторите попытку.")
            if not flag_speed and not flag_port:
                self.text_terminal.setText(
                    "Вы не выбрали ни порт, ни скорость порта. Выберите нужный вам и порт и скорость этого порта. Поторите попытку.")

    def on_progress(self, value):
        print(value)

    def on_finished(self):
        self.thread.progressed.disconnect(self.on_progress)
        self.thread.finished.disconnect(self.on_finished)
        self.thread = None

    def valuechange(self, value):
        self.speed = value
        # print("__init__vSl -> ", self.speed)
        self.thread.speed = self.speed
        return self.size

    def button_get_info_trackers(self):
        self.w2 = Window2()
        self.w2.show()

    def button_start(self):
        global flag_start
        if flag_start:
            self.sld.setEnabled(True)
            self.get_info_trackers.setEnabled(True)
            self.start.setEnabled(False)
            self.current_speed_ports.setEnabled(False)
            self.current_COM_port.setEnabled(False)
            self.pushButton.setEnabled(False)
            self.thread = SerialThread()
            self.thread.start()
            if not self.thread:
                self.thread.progressed.connect(self.on_progress)
                self.thread.finished.connect(self.on_finished)
                self.thread.start()

        else:
            self.text_terminal.setText(
                "Вы не выбрали либо порт, либо скорость порта, повторите попытку.")

    def button_stop(self):
        global x, flag_stop
        if flag_start:
            flag_stop = False
            self.sld.setEnabled(False)

            # self.sld.setValue(0)
            # self.result.display(0)
            # self.thread.stop()
            # sys.exit(app.exec_())
        else:
            self.text_terminal.setText(
                "Данных на arduino пока не поступало.")

    def add_head(self):
        if self.head.text() not in self.list_need_trackers:
            self.list_need_trackers.append(self.head.text())
        else:
            pass

    def add_L_hand(self):
        if self.L_hand.text() not in self.list_need_trackers:
            self.list_need_trackers.append(self.L_hand.text())
        else:
            pass

    def add_L_leg(self):
        if self.L_leg.text() not in self.list_need_trackers:
            self.list_need_trackers.append(self.L_leg.text())
        else:
            pass

    def add_R_leg(self):
        if self.R_leg.text() not in self.list_need_trackers:
            self.list_need_trackers.append(self.R_leg.text())
        else:
            pass

    def add_R_hand(self):
        if self.R_hand.text() not in self.list_need_trackers:
            self.list_need_trackers.append(self.R_hand.text())
        else:
            pass


app = QApplication(sys.argv)

ex = Sliderdemo()
ex.show()
sys.exit(app.exec_())
