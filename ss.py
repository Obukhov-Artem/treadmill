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

CURRENT_ACTION = 0
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
        for device in v.devices:
            position_device = v.devices[device].sample(1, 500)

            if position_device:
                print(v.devices[device].get_serial(),position_device.get_position_x(),position_device.get_position_y())
                if position_device.get_position_x()[0] > 0 and position_device.get_position_y()[0] > 0.3 and position_device.get_position_y()[0] < 1:
                    right_knee = (v.devices[device].get_serial(),v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] < 0 and position_device.get_position_y()[0] > 0.3 and position_device.get_position_y()[0] < 1:
                    left_knee = (v.devices[device].get_serial(),v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] > 0 and position_device.get_position_y()[0] < 0.3:
                    right_leg = (v.devices[device].get_serial(),v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] < 0 and position_device.get_position_y()[0] < 0.3:
                    left_leg = (v.devices[device].get_serial(),v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] > 0 and position_device.get_position_y()[0] > 1:
                    right_hand = (v.devices[device].get_serial(),v.device_index_map[v.devices[device].index])
                if position_device.get_position_x()[0] < 0 and position_device.get_position_y()[0] > 1:
                    left_hand = (v.devices[device].get_serial(),v.device_index_map[v.devices[device].index])
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
        data = []
        print(self.slovar_trackers)
        while n<5:

            data_current = []
            for serial in self.slovar_trackers:
                if self.slovar_trackers[serial]:
                    try:
                        print(self.slovar_trackers[serial])
                        current_serial, device = self.slovar_trackers[serial]
                        position_device = v.devices[device].sample(1, 50)

                        if position_device:
                            c = position_device.get_position()
                            if current_serial != 'LHR-3A018118' and \
                                    current_serial != 'LHR-1A2114EA':
                                '''Get_data_trackers.csv_writer('p.csv', Get_data_trackers.fieldnames, 
                                                             position_device.get_position())'''  # 1 Вариант записи в csv
                                data_current.extend([c[0][0],c[1][0],c[2][0]])

                    except Exception as e:
                        print(e)
                        #if n>0:
                        #    data_current.append(data_current[n - 1][num_device])

            data_current.append(CURRENT_ACTION)
            data.append(data_current)
            n +=1
        print(data)
        self.csv_writer('p.csv', self.fieldnames,
                                     data)  # 2 Вариант записи в csv


if __name__ == '__main__':
    ex = Get_data_trackers()
    ex.get_info()
