import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QSlider, QApplication, QTextBrowser)
import sys
import serial
import time
import serial.tools.list_ports
import glob


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

    print("Loading...")
    return __COMlist


def CheckSerialPortMessage(__activeCOM=Search(), __baudrate=115200, __timeSleep=5):
    global current_port
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

                        if ('treadmill' in date):
                            try:
                                current_port = __COM
                                return __COM
                                break
                            except Exception as e:
                                return e
                        else:
                            continue
                    else:
                        break
                break
    except Exception as e:
        return e


CheckSerialPortMessage()


class SerialThread(QThread):
    def __init__(self):
        super().__init__()
        self.speed_treadmill = 0
        port = serial.Serial(self.current_port, self.current_speed)
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
        x = str(self.speed_treadmill) + '.'
        self.port.write(bytes(x, 'utf-8'))
        print(self.port.readline())


class Sliderdemo(QMainWindow):
    speed_signal = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        uic.loadUi('int.ui', self)
        self.initUI()

    def initUI(self):
        vSl = 1
        self.speed_treadmill = 1
        self.setWindowTitle('Тестовывй режим')
        self.start.clicked.connect(self.button_start)
        self.current_speed_ports.clicked.connect(self.transform_selection)
        self.current_COM_port.clicked.connect(self.source_unit)
        self.speed_treadmill = QSlider(Qt.Horizontal, self)
        self.pushButton.clicked.connect(self.button_connection)
        self.speed_treadmill.setGeometry(250, 240, 161, 22)
        self.speed_treadmill.setMinimum(0)
        self.speed_treadmill.setTickInterval(1)
        self.speed_treadmill.setMaximum(255)
        self.speed_treadmill.setValue(vSl)
        self.speed_treadmill.setTickInterval(10)
        self.speed_treadmill.valueChanged.connect(self.result.display)
        self.show()

    def get_dialog(self, from_=True):
        try:
            self.current_port, okBtnPressed = QInputDialog.getItem(self, "Выберите COM-порт", "Доступные COM-Порты",
                                                   Search(), 0, False)
        except Exception as e:
            print(e)
        '''if okBtnPressed:
            if from_:
                self.source.setText("Исходная единица:" + i)
                self.from_ = i
            else:
                try:

                    self.new_2.setText("Новая единица:" + i)
                    self.to_ = i
                    self.result.display(self.speed)
                except Exception:
                    pass'''

    def transform_selection(self):
        speeds = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
        self.current_speed, okBtnPressed = QInputDialog.getItem(self, "Выберите скорость", "Доступные скорости",
                                                           speeds, 0, False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Enter - 1:
            try:
                self.result.display(self.speed_treadmill)
            except Exception:
                pass

    def source_unit(self):
        self.get_dialog(True)

    def new_unit(self):
        self.get_dialog(False)

    def button_connection(self):
        try:
            self.pushButton.setText('Подключено')
        except Exception as e:
            self.pushButton.setText(e)
            print(e)

    def button_start(self):
        self.thread = SerialThread()
        self.thread.start()
        if not self.thread:
            # self.thread = SerialThread(ports[0])
            self.thread.progressed.connect(self.on_progress)
            self.thread.finished.connect(self.on_finished)
            self.thread.start()


app = QApplication(sys.argv)

ex = Sliderdemo()
ex.show()
sys.exit(app.exec_())
