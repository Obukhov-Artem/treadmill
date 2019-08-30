import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider, QVBoxLayout, QApplication)
import sys
import glob
import serial
import time
# from testSlider import data_in_arduino
import csv
import triad_openvr
import threading
import socket

UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', UDP_PORT))

while True:
    data = sock.recv(1024)
    if not data:
        break
    print(data)

sock.close()

# print(data_in_arduino)
CURRENT_ACTION = 0


# CURRENT_ACTION = data_in_arduino


class Get_data_trackers():
    def __init__(self):
        self.fieldnames = ['x_tracker_1', 'y_tracker_1', 'z_tracker_1',
                           'x_tracker_2', 'y_tracker_2', 'z_tracker_2',
                           'x_tracker_3', 'y_tracker_3', 'z_tracker_3',
                           'x_tracker_4', 'y_tracker_4', 'z_tracker_4',
                           'data_on_treadmill']
        self.calibration()

    def csv_writer(self, path, fieldnames, data):
        with open(path, "w", newline='') as out_file:
            writer = csv.writer(out_file, delimiter=';')
            writer.writerow(fieldnames)
            for row in data:
                writer.writerow(row)

    def calibration(self):
        v = triad_openvr.triad_openvr()
        print(v.devices)
        right_hand = None
        right_knee = None
        right_leg = None
        left_hand = None
        left_knee = None
        left_leg = None
        pos_devices_array = []
        for device in v.devices:
            position_device = v.devices[device].sample(1, 500)

            if position_device:
                pos_devices_array.append((position_device.get_position_x()[0], position_device.get_position_y()[0],
                                          v.devices[device].get_serial(), v.device_index_map[v.devices[device].index]))
                """
                print(v.devices[device].get_serial(), position_device.get_position_x(),
                      position_device.get_position_y())
                if position_device.get_position_x()[0] > 0 and position_device.get_position_y()[0] > 0.3 and \
                        position_device.get_position_y()[0] < 1:
                    right_knee = (v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] < 0 and position_device.get_position_y()[0] > 0.3 and \
                        position_device.get_position_y()[0] < 1:
                    left_knee = (v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] > 0 and position_device.get_position_y()[0] < 0.4:
                    right_leg = (v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] < 0 and position_device.get_position_y()[0] < 0.4:
                    left_leg = (v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] > 0 and position_device.get_position_y()[0] > 1:
                    right_hand = (v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] < 0 and position_device.get_position_y()[0] > 1:
                    left_hand = (v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                    """
        p_a = sorted(pos_devices_array, key=lambda x: x[1])
        print(len(p_a), p_a)
        if len(p_a) > 2:
            if p_a[0][1] < 0.5 and p_a[1][1] < 0.5:
                if p_a[0][0] < p_a[1][0]:
                    left_leg = (p_a[0][2], p_a[0][3])
                    right_leg = (p_a[1][2], p_a[1][3])
                else:
                    right_leg = (p_a[0][2], p_a[0][3])
                    left_leg = (p_a[1][2], p_a[1][3])
        if len(p_a) > 4:
            if p_a[2][1] >= 0.5 and p_a[3][1] >= 0.5:
                if p_a[2][0] < p_a[3][0]:
                    left_leg = (p_a[2][2], p_a[2][3])
                    right_leg = (p_a[3][2], p_a[3][3])
                else:
                    right_leg = (p_a[2][2], p_a[2][3])
                    left_leg = (p_a[3][2], p_a[3][3])
        if len(p_a) > 6:
            if p_a[4][1] >= 1 and p_a[5][1] >= 1:
                if p_a[4][0] < p_a[4][0]:
                    left_leg = (p_a[4][2], p_a[4][3])
                    right_leg = (p_a[5][2], p_a[5][3])
                else:
                    right_leg = (p_a[4][2], p_a[4][3])
                    left_leg = (p_a[5][2], p_a[5][3])

        self.slovar_trackers = {"Правое_колено": right_knee,
                                "Левое_колено": left_knee,
                                "Правая_голень": right_leg,
                                "Левая_голень": left_leg,
                                "Правая_перчатка": right_hand,
                                "Левая_перчатка": left_hand}

    def get_info(self):
        v = triad_openvr.triad_openvr()
        v.print_discovered_objects()
        n = 0
        a = 0
        data = []
        print(self.slovar_trackers)
        while n < 3000:

            data_current = []
            for serial in self.slovar_trackers:
                if self.slovar_trackers[serial]:
                    try:
                        # print(self.slovar_trackers[serial])
                        current_serial, device = self.slovar_trackers[serial]
                        position_device = v.devices[device].sample(1, 20)
                        if position_device:
                            c = position_device.get_position()
                            data_current.extend([c[0][0], c[1][0], c[2][0]])

                    except Exception as e:
                        print(e)
                        # if n>0:
                        #    data_current.append(data_current[n - 1][num_device])

            data_current.append(data)
            data.append(data_current)
            print(data_current)
            n += 1

        '''while a < 100:
            a += 1
            print(data)
            self.csv_writer('p0.csv', self.fieldnames,
                            data)  # 2 Вариант записи в csv

        print(data)'''
        self.csv_writer('p_1.csv', self.fieldnames,
                        data)


if __name__ == '__main__':
    ex = Get_data_trackers()
    ex.get_info()
