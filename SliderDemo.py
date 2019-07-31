from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider, QVBoxLayout, QApplication)
import sys
import glob
import serial
import time
import serial.tools.list_ports

'''ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)'''
current_port = ''
class SerialThread(QThread):
    speed_signal = pyqtSignal(bytes)

    def Search(__baudrate=115200, timeSleep=5):
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

        print("SearchSerialPort__COMlist = ", __COMlist)
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

                                print(__COM)
                                current_port = __COM
                                return __COM
                                break
                            else:
                                continue
                        else:
                            break
                    break
        except Exception as e:
            return e
    CheckSerialPortMessage()

    def __init__(self):
        global current_port
        super().__init__()
        self.speed = 1
        port = serial.Serial(current_port, 115200)
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
        x = str(self.speed) + '.'
        self.port.write(bytes(x, 'utf-8'))
        print(self.port.readline())


class Sliderdemo(QWidget):
    def __init__(self, vSl=1, parent=None):
        super(Sliderdemo, self).__init__(parent)
        self.speed = 1
        lcd = QLCDNumber(self)
        lcd.display(1)
        vbox = QVBoxLayout()
        sld = QSlider(Qt.Horizontal, self)
        sld.setMinimum(0)
        sld.setTickInterval(1)
        sld.setMaximum(255)
        sld.setValue(1)
        sld.setTickPosition(QSlider.TicksBelow)
        sld.setTickInterval(10)
        vbox.addWidget(lcd)
        vbox.addWidget(sld)
        self.realport = None
        sld.valueChanged[int].connect(self.valuechange)
        self.setLayout(vbox)
        sld.valueChanged.connect(lcd.display)
        self.setWindowTitle("Тестовый режим")
        # print(self.valuechange())
        self.thread = SerialThread()
        self.thread.start()

        if not self.thread:
            # self.thread = SerialThread(ports[0])
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
        # print("__init__vSl -> ", self.speed)
        self.thread.speed = self.speed
        return self.size


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Sliderdemo(32)
    ex.show()
    sys.exit(app.exec_())
