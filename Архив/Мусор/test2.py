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

    def __init__(self,port):
        super().__init__()
        self.speed = 32
        port = serial.Serial('COM3', 115200)
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
        x = str(self.speed)
        self.port.write(bytes(x, 'utf-8'))
        print(self.port.readline())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SerialThread(32)
    sys.exit(app.exec_())
