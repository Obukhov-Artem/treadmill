import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider, QVBoxLayout, QApplication)
import sys
import glob
import time
# from testSlider import data_in_arduino
import csv
import triad_openvr
import threading
import socket
from keras.models import load_model
import numpy as np

UDP_IP = "192.168.0.115"
UDP_PORT_Rec = 3040
UDP_PORT_Unity = 3021
import socket

conn = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
conn.bind(('',UDP_PORT_Rec))
class Get_data_trackers():
    def __init__(self):
        self.fieldnames = ['x_tracker_1', 'y_tracker_1', 'z_tracker_1',
                           'x_tracker_2', 'y_tracker_2', 'z_tracker_2',
                           'x_tracker_3', 'y_tracker_3', 'z_tracker_3',
                           'x_tracker_4', 'y_tracker_4', 'z_tracker_4',
                           'data_on_treadmill']
        self.calibration()
        self.NN = None

    def set_NN(self, model,model2=None):

        self.NN = load_model(model)
        self.NN2 = load_model(model2)

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
        # v.print_discovered_objects()
        # print(self.slovar_trackers)
        data_current = []
        for serial in self.slovar_trackers:
            if self.slovar_trackers[serial]:
                try:
                    current_serial, device = self.slovar_trackers[serial]
                    position_device = v.devices[device].sample(1, 20)
                    if position_device:
                        c = position_device.get_position()

                        data_current.extend([c[0][0], c[1][0], c[2][0]])

                except Exception as e:
                    print(e)
        return data_current

    def predict_data(self, data):
        new_data = self.NN2.predict(data)
        return new_data

    def predict_speed(self, data):
        new_data = self.NN.predict(data)
        return new_data


if __name__ == '__main__':

    n = 0
    data = []
    flag = False
    ex = Get_data_trackers()
    ex.set_NN('NN_speed7931.h5', 'NN_predict7931.h5')
    start = time.time()
    while True:
        if time.time() > start + 1 / 25:
            start = time.time()
            if n < 5:
                data.append(ex.get_info())
            else:
                delta = []
                data.append(ex.get_info())
                for i in range(1, len(data)):
                    current = []
                    for j in range(0, 6):
                        current.append(data[i][j] - data[i - 1][j])
                    delta.append(current)
                data = data[1:]
                X = np.array(delta)
                # print(delta)
                future_data = ex.predict_data(X.reshape(-1, 5, 6))
                print(future_data.shape)
                y = ex.predict_speed(future_data[10:,:])
                print(np.argmax(y))
                if y>0.3:
                    conn.sendto(bytes(str(int(1)).rjust(4," "), 'utf-8'), (UDP_IP, UDP_PORT_Unity))
                else:
                    conn.sendto(bytes(str(int(0)).rjust(4," "), 'utf-8'), (UDP_IP, UDP_PORT_Unity))

                    # Отправка данных на дорожку по сокетам
            n += 1
