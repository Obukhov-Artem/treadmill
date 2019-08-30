import serial
import threading
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider, QVBoxLayout, QApplication)
import sys
import glob
import serial
import time
import csv
import triad_openvr
import threading
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


    def valuechange(self, value):
        global speed
        self.speed = value
        #print("__init__vSl -> ", self.speed)
        speed = value
        # return self.size

app = QApplication(sys.argv)
ex = Sliderdemo(32)

class TestThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        app.exec_()
        ex.show()



speed = 100
port = serial.Serial(port=str('COM3'),
                     baudrate=115200,
                     timeout=0)
thread=TestThread()
thread.start()
thread.run()
print(1)
while True:
    #speed = input()
    x = str(speed) + '.'
    print(x)
    port.write(bytes(x, 'utf-8'))

