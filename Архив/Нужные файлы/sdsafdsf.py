import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QSlider, QApplication, QVBoxLayout)
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QMenuBar, QApplication
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal
import sys
import serial
import time
import serial.tools.list_ports
import glob
import socket

current_port = ''
current_speed = ''
flag_port = False
flag_speed = False
flag_start = False
flag_stop = True
flag_reload = False
flag_increase_speed = False
stop_speed = 0
x = 0
data_in_arduino = 0
print('Loading...')

UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(('localhost', UDP_PORT))


def Search(__baudrate=115200, timeSleep=5):
    speed_signal = pyqtSignal(bytes)

    # Port Database
    __COMlist = []
    __COM = ['COM' + str(i) for i in range(2, 100)]

    for _COM in __COM:
        try:
            COMport = (serial.Serial(port=_COM, \
                                     baudrate=__baudrate, \
                                     parity=serial.PARITY_NONE, \
                                     stopbits=serial.STOPBITS_ONE, \
                                     bytesize=serial.EIGHTBITS, \
                                     timeout=0))

            if COMport:
                # COMlist Creation
                __COMlist.append(_COM)
            else:
                pass

        except Exception as e:
            '''ErrorAttachment = open("SerialErrorAttachment.txt", "a")
            ErrorAttachment.write(e.__class__.__name__ + "\r")
            ErrorAttachment.close()'''
            continue
    return __COMlist


def CheckSerialPortMessage(__activeCOM=Search(), __baudrate=115200, __timeSleep=5):
    try:
        for __COM in __activeCOM:

            port = serial.Serial(__COM, __baudrate)
            time.sleep(__timeSleep)
            large = len(port.readline())
            port.read(large)

            while True:

                if large > 3:
                    for a in range(__timeSleep):

                        date = port.readline().decode().split()

                        if 'treadmill' in date:
                            return __COM

                else:
                    break

    except Exception as e:
        return e


CheckSerialPortMessage()


class SerialThread(QThread):
    def __init__(self):
        global current_speed, current_port
        super().__init__()
        self.speed = 0
        self.speed2 = 0
        port = serial.Serial(current_port, current_speed)
        self.port = port
        self.rt = None
        self.start()

    def run(self):
        while True:
            if self.speed < self.speed2:
                self.speed += 2
            if self.speed > self.speed2:
                self.speed -= 2
            self.write_to_port()
            time.sleep(0.1)
            '''                                     # Доработать кореектное изменение скорости. 
            a = self.speed - self.speed2
            if a <= 40:
                self.speed += 2
            if a <= 20 and a < 40:
                self.speed += 1
            if a > 20 and a < 0:
                pass
            if a >= -40:
                self.speed -= 2
            if a >= -20 and a < -40:
                self.speed -= 1
            if a > -20 and a < 0:
                pass
            if self.speed > self.speed2:
                self.speed -= 1
                '''

    def stop(self):
        if self.rt:
            self.rt.join()

    def write_to_port(self):
        if flag_stop:
            x = str(self.speed) + '.'
        if not flag_stop:
            if self.speed != 0:
                self.speed -= 1
                self.speed2 = self.speed
                x = str(self.speed) + '.'
            else:
                x = str(0) + '.'
        self.port.write(bytes(x, 'utf-8'))
        a = x.replace('.', '')
        sock.send(bytes(str(a), 'utf-8'))
        print(self.port.readline())


class Sliderdemo(QMainWindow):
    speed_signal = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        uic.loadUi('int.ui', self)
        self.initUI()

    def initUI(self):
        global stop_speed
        self.start.clicked.connect(self.button_start)
        self.reload.clicked.connect(self.button_reload)
        self.current_speed_ports.clicked.connect(self.transform_selection)
        self.current_COM_port.clicked.connect(self.get_dialog)
        self.pushButton.clicked.connect(self.button_connection)
        self.stop.clicked.connect(self.button_stop)
        self.setWindowTitle("Тестовый режим")
        self.result.display(0)
        self.text_terminal.setText(
            "       Проверка подключения")
        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setGeometry(250, 330, 160, 22)
        self.sld.setMinimum(0)
        self.sld.setTickInterval(1)
        self.sld.setMaximum(255)
        self.sld.setValue(0)
        self.sld.setTickPosition(QSlider.TicksBelow)
        self.sld.setTickInterval(10)
        self.sld.valueChanged[int].connect(self.valuechange)
        self.sld.valueChanged.connect(self.result.display)
        self.sld.setEnabled(False)
        self.reload.setEnabled(False)
        vbox = QVBoxLayout()
        vbox.addWidget(self.result)
        vbox.addWidget(self.sld)
        self.show()

    def get_dialog(self):
        global current_port, flag_port
        current_port, flag_port = QInputDialog.getItem(self, "Выберите COM-порт",
                                                       "Доступные COM-Порты",
                                                       Search(), 0, False)
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
        self.thread.speed2 = self.speed
        return self.size

    def button_start(self):
        global flag_start, flag_increase_speed
        if flag_start:
            self.sld.setEnabled(True)
            self.start.setEnabled(False)
            self.current_speed_ports.setEnabled(False)
            self.current_COM_port.setEnabled(False)
            self.pushButton.setEnabled(False)
            self.thread = SerialThread()
            flag_increase_speed = True
            self.thread.start()
            if not self.thread:
                self.thread.progressed.connect(self.on_progress)
                self.thread.finished.connect(self.on_finished)
                flag_increase_speed = True
                self.thread.start()

        else:
            self.text_terminal.setText(
                "Вы не выбрали либо порт, либо скорость порта, повторите попытку.")

    def button_stop(self):
        global x, flag_stop
        self.stop.setEnabled(False)
        if flag_start:
            flag_stop = False
            self.sld.setEnabled(False)
            self.reload.setEnabled(True)

            # self.sld.setValue(0)
            # self.result.display(0)
            # self.thread.stop()
            # sys.exit(app.exec_())
        else:
            self.text_terminal.setText(
                "Данных на arduino пока не поступало.")

    def button_reload(self):
        global flag_start, flag_stop, flag_reload
        flag_reload = True
        self.stop.setEnabled(True)
        flag_stop = True
        self.result.display(0)
        self.speed = 0
        self.sld.setValue(0)
        self.reload.setEnabled(False)
        self.sld.setEnabled(True)

class OutputLogger(QObject):
    emit_write = Signal(str, int)

    class Severity:
        DEBUG = 0
        ERROR = 1

    def __init__(self, io_stream, severity):
        super().__init__()

        self.io_stream = io_stream
        self.severity = severity

    def write(self, text):
        self.io_stream.write(text)
        self.emit_write.emit(text, self.severity)

    def flush(self):
        self.io_stream.flush()


import sys
OUTPUT_LOGGER_STDOUT = OutputLogger(sys.stdout, OutputLogger.Severity.DEBUG)
OUTPUT_LOGGER_STDERR = OutputLogger(sys.stderr, OutputLogger.Severity.ERROR)

sys.stdout = OUTPUT_LOGGER_STDOUT
sys.stderr = OUTPUT_LOGGER_STDERR


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.text_edit = QTextEdit()

        OUTPUT_LOGGER_STDOUT.emit_write.connect(self.append_log)
        OUTPUT_LOGGER_STDERR.emit_write.connect(self.append_log)


        self.setCentralWidget(self.text_edit)

    def append_log(self, text, severity):
        text = repr(text)

        if severity == OutputLogger.Severity.ERROR:
            self.text_edit.append('<b>{}</b>'.format(text))
        else:
            self.text_edit.append(text)


app = QApplication(sys.argv)
ex = Sliderdemo()
ex.show()
mw = MainWindow()
mw.show()
sys.exit(app.exec_())
