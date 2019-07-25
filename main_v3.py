import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider, QVBoxLayout, QApplication)
import sys
import glob
import serial
import time
import csv
import triad_openvr
import threading


class SerialThread(QThread):
    speed_signal = pyqtSignal(bytes)

    def __init__(self, port):
        super().__init__()
        self.speed = 32
        self.port = port
        self.rt = None
        self.start()

    def run(self):
        self.write_to_port()

    def run1(self):
        while True:
            self.write_to_port()
            # print(self.speed)
            time.sleep(0.1)

    def start(self):
        self.rt = threading.Thread(target=self.run1)
        self.rt.start()

    def stop(self):
        if self.rt:
            self.rt.join()

    def write_to_port(self):
        port = serial.Serial(port=str('COM3'),
                             baudrate=11520,
                             parity=serial.PARITY_NONE,
                             stopbits=serial.STOPBITS_ONE,
                             bytesize=serial.EIGHTBITS,
                             timeout=0)
        port.write(bytes(str(self.speed) + '.'))
        print((str(self.speed) + '.'))
        print(port.readall())

class TestThread(QThread):
    def __init__(self):
        super().__init__()
        self.speed = 32

    def run(self):
        while True:
            self.write_to_port()
            time.sleep(0.1)

    def write_to_port(self):
        port = serial.Serial(port=str('COM3'),
                             baudrate=115200,
                             dsrdtr=1,
                             timeout=0,
                             rtscts=True,
                             parity=serial.PARITY_NONE,
                             stopbits=serial.STOPBITS_ONE,
                             bytesize=serial.EIGHTBITS,
                             xonxoff=False)
        x = str(self.speed)
        port.write(bytes(x))
        print(port.readline())

class Sliderdemo(QWidget):

    def __init__(self, vSl=32, parent=None):
        super(Sliderdemo, self).__init__(parent)
        lcd = QLCDNumber(self)
        lcd.display(32)
        vbox = QVBoxLayout()
        sld = QSlider(Qt.Horizontal, self)
        sld.setMinimum(32)
        sld.setTickInterval(1)
        sld.setMaximum(255)
        sld.setValue(vSl)
        sld.setTickPosition(QSlider.TicksBelow)
        sld.setTickInterval(10)
        vbox.addWidget(lcd)
        vbox.addWidget(sld)
        sld.valueChanged[int].connect(self.valuechange)
        self.setLayout(vbox)
        sld.valueChanged.connect(lcd.display)
        self.setWindowTitle("Тестовый режим")
        # print(self.valuechange())
        self.thread = TestThread()
        self.thread.start()

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
        # return self.size

    """def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(25)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        #s = serial.Serial('COM3', 9600)
        for port in ports:
            try:
                s = serial.Serial('COM3', 9600)
                s.close()
                result.append(port)
            except Exception as se:
                print(se)
        return"""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Sliderdemo(32)
    ex.show()
    sys.exit(app.exec_())
