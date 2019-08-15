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
              'speed']


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
        self.slovar_trackers = {"Правое_колено": right_knee,  # tracker_1
                                "Левое_колено": left_knee,  # tracker_2
                                "Правая_голень": right_leg,  # tracker_3
                                "Левая_голень": left_leg,  # tracker_4
                                "Правая_перчатка": right_hand,  # tracker_5
                                "Левая_перчатка": left_hand}  # tracker_6
    return self.slovar_trackers


def get_info(self):
    v = triad_openvr.triad_openvr()
    v.print_discovered_objects()
    n = 0
    data = []
    data_current = []
    for serial in self.slover_trackers():
        device, num_device = self.slover_trackers[serial]
        try:
            position_device = v.devices[device].sample(1, 500) + str(SerialThread.speed)
            if position_device and n > 0:
                if v.devices[device].get_serial() != 'LHR-3A018118' and \
                        v.devices[device].get_serial() != 'LHR-1A2114EA':
                    csv_writer('p.csv', fieldnames,
                               position_device.get_position())
                    data_current.append(position_device.get_position())  # 1 Вариант записи в csv

        except Exception as e:
            data_current.append(data_current[n - 1][num_device])
            pass
    data.append(data_current)
    csv_writer('p.csv', fieldnames, data)  # 2 Вариант записи в csv
