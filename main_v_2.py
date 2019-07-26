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

    def __init__(self, port='COM3'):
        super().__init__()
        self.speed = 32
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
        port = serial.Serial('COM3', 115200)
        x = str(self.speed) + '.'
        port.write(bytes(x, 'utf-8'))
        print(port.readline())
        print(self.speed)


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
                             timeout=0)
        x = str(self.speed) + '.'
        # port.write(bytes(x, 'utf-8'))
        port.write("100.".encode('utf-8'))
        print(port.readall())


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
        ports = self.serial_ports()
        """if ports:
            print(ports)

            if not self.thread:
                self.thread = SerialThread(ports[0])
                self.thread.progressed.connect(self.on_progress)
                self.thread.finished.connect(self.on_finished)
                self.thread.start()
        """

    def on_progress(self, value):
        print(value)

    def on_finished(self):
        self.thread.progressed.disconnect(self.on_progress)
        self.thread.finished.disconnect(self.on_finished)
        self.thread = None

    def valuechange(self, value):
        self.speed = value
        print("__init__vSl -> ", self.speed)
        self.thread.speed = self.speed
        # return self.size

    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(25)]
        '''elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
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
                print(se)'''
        return


# Сбор информации о трекерах
class Get_data():
    slovar_trackers = {"tracker_1": 'LHR-3A018118',
                       "tracker_2": 'LHR-9224071E',
                       "tracker_3": 'LHR-89FBFC40',
                       "tracker_4": 'LHR-1761CD18',
                       "tracker_5": 'right_hand',
                       "tracker_6": 'left_hand'}

    fieldnames = ['x_tracker_1', 'y_tracker_1', 'z_tracker_1',
                  'x_tracker_2', 'y_tracker_2', 'z_tracker_2',
                  'x_tracker_3', 'y_tracker_3', 'z_tracker_3',
                  'x_tracker_4', 'y_tracker_4', 'z_tracker_4',
                  'data_on_treadmill']

    def csv_writer(path, fieldnames, data):
        with open(path, "w", newline='') as out_file:
            writer = csv.DictWriter(out_file, delimiter=';', fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

    def calibration(self):
        v = triad_openvr.triad_openvr()
        for device in v.devices:
            position_device = v.devices[device].sample(1, 500)
            if position_device.get_position_x > 0 and position_device.get_position_y > 0.3 and position_device.get_position_y < 1:
                right_knee = v.devices[device].get_serial()
            if position_device.get_position_x < 0 and position_device.get_position_y > 0.3 and position_device.get_position_y < 1:
                left_knee = v.devices[device].get_serial()
            if position_device.get_position_x > 0 and position_device.get_position_y < 0.3:
                right_leg = v.devices[device].get_serial()
            if position_device.get_position_x < 0 and position_device.get_position_y < 0.3:
                left_leg = v.devices[device].get_serial()
            if position_device.get_position_x > 0 and position_device.get_position_y > 1:
                right_hand = v.devices[device].get_serial()
            if position_device.get_position_x < 0 and position_device.get_position_y > 1:
                left_hand = v.devices[device].get_serial()
            self.slovar_trackers = {"tracker_1": right_knee,
                                    "tracker_2": left_knee,
                                    "tracker_3": right_leg,
                                    "tracker_4": left_leg,
                                    "tracker_5": right_hand,
                                    "tracker_6": left_hand}
        return self.slovar_trackers

    def getinfo(self):
        v = triad_openvr.triad_openvr()
        v.print_discovered_objects()
        n = 0
        data = []
        data_current = []
        for serial in self.slover_trackers():
            device, num_device = self.slover_trackers[serial]
            try:
                position_device = v.devices[device].sample(1, 500)
                if position_device and n > 0:
                    '''Get_data.csv_writer('p.csv', Get_data.fieldnames, position_device.get_position())'''
                    data_current.append(position_device.get_position())
            except Exception as e:
                data_current.append(data_current[n - 1][num_device])
                pass
        data.append(data_current)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Sliderdemo(32)
    ex.show()
    sys.exit(app.exec_())
