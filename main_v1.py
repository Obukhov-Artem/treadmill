import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider, QVBoxLayout, QApplication)
import sys
import glob
import serial
import time


class SerialThread(QThread):
    speed_signal = pyqtSignal(bytes)

    def __init__(self, port):
        super().__init__()
        self.speed = 32
        self.port = port

    def run(self):
        self.write_to_port()

    def write_to_port(self):
        port = serial.Serial(port=str(self.port), \
                             baudrate=115200, \
                             parity=serial.PARITY_NONE, \
                             stopbits=serial.STOPBITS_ONE, \
                             bytesize=serial.EIGHTBITS, \
                             timeout=0)
        port.write(bytes(self.speed))

class TestThread(QThread):

    def __init__(self):
        super().__init__()
        self.speed=0

    def run(self):
        while True:
            print(self.speed)
            time.sleep(0.1)




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
        self.setWindowTitle("slider")
        # print(self.valuechange())
        self.tthead = TestThread()
        self.tthead.start()
        self.speed = 32
        self.thread = None
        ports = self.serial_ports()
        if ports:
            print(ports)

            if not self.thread:
                self.thread = SerialThread(ports[0])
                self.thread.progressed.connect(self.on_progress)
                self.thread.finished.connect(self.on_finished)
                self.thread.start()

    def on_progress(self, value):
        print(value)

    def on_finished(self):
        self.thread.progressed.disconnect(self.on_progress)
        self.thread.finished.disconnect(self.on_finished)
        self.thread = None

    def valuechange(self, value):
        self.speed = value
        print("__init__vSl -> ", self.speed)
        self.tthead.speed = self.speed
        # return self.size


    def serial_ports(self):
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
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except Exception as se:
                print(se)
        return result


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Sliderdemo(32)
    ex.show()
    sys.exit(app.exec_())
