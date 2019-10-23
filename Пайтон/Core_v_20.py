import serial.tools.list_ports
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
# version 12.2
import triad_openvr
import threading
import asyncio
import serial
import time
import sys
import csv
import math
import socket

u = 0
SERIAL = 'LHR-1761CD18'
drag_coefficient = 255
max_speed = 255
__baudrate = 115200
arduino = None
current_speed = 0
last_speed = 0
slovar_trackers = {}
MainWhile = True
human_0 = None
UDP_PORT = 3021
UDP_PORT_Rec = 3040
ip = "192.168.0.115"
conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
conn.bind(('',UDP_PORT_Rec))
def push(speed):

    print("--------------")
    print("--------------")
    print(speed)
    print(conn.sendto((bytes(str(speed), 'utf-8')), (ip, UDP_PORT)))
    conn.settimeout(0.1)
    print("--------------")
    print()
    print()

def calibration():
        global human_0,slovar_trackers
        z_napr = 1
        v = triad_openvr.triad_openvr()
        human_pos = None
        hmd_pos = None
        human_0 = None
        pos_devices_array = []
        n = 1
        while n > 0 and human_pos is None:
            n -= 1
            for device in v.devices:
                position_device = v.devices[device].sample(1, 500)

                if position_device:

                    if v.devices[device].device_class == 'HMD':
                        hmd_pos = (position_device.get_position_x()[0], position_device.get_position_y()[0],
                                   position_device.get_position_z()[0],
                                   v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                    else:
                        pos_devices_array.append(
                            (position_device.get_position_x()[0], position_device.get_position_y()[0],
                             position_device.get_position_z()[0],
                             v.devices[device].get_serial(),
                             v.device_index_map[v.devices[device].index]))
                        print(v.devices[device].get_serial())
                        if v.devices[device].get_serial() == SERIAL:
                            print("OK")
                            human_0 = [position_device.get_position_x()[0], position_device.get_position_y()[0],
                                            position_device.get_position_z()[0]]
                            human_pos = (v.devices[device].get_serial(),
                                         v.device_index_map[v.devices[device].index])

            p_a = sorted(pos_devices_array, key=lambda x: x[1])
            print(p_a)
        slovar_trackers = {"Человек": human_pos}



def get_speed(z):
    safe_zona = 0.2
    tr_len = 0.4
    if z < 0:
        zn = -1
    else:
        zn = 1
    z = abs(z)
    if z < safe_zona:
        print("safe zona")
        return 0
    elif safe_zona <= z <= tr_len:
        delta = tr_len - safe_zona
        if z * drag_coefficient <= max_speed:
            speed = (z - safe_zona) * max_speed / (delta)

            delta_speed = abs(zn * min(max_speed, speed)) - abs(last_speed)
            print("*******", delta_speed)
            if delta_speed < -0.5:
                ks = 1.3
                print("work zona - TORMOZHENIE")
            else:
                ks = 1

            print("work zona")
            return zn * min(max_speed, speed * ks)
        else:

            print("far zona speed")
            return zn * max_speed
    elif z > tr_len:
        print("far zona")
        return zn * max_speed
    else:
        print("error")
        return 0


def ExtremeStop():  # problem
    global current_speed,MainWhile,last_speed
    print("*" * 10, "Extreme stop", current_speed)
    arduino.write(bytes(str('d') + '.', 'utf-8'))
    if current_speed > 0:
        while current_speed > 0:
            current_speed -= 2
            print("extreme", current_speed)
            arduino.write(bytes(str(int(max(current_speed, 0))) + '.', 'utf-8'))
            print(str(int(max(current_speed, 0))) + '.')
            time.sleep(0.05)
    else:

        while current_speed < 0:
            current_speed += 2
            print("extreme", current_speed)
            arduino.write(bytes(str(int(min(current_speed, 0))) + '.', 'utf-8'))
            print(str(int(min(current_speed, 0))) + '.')
            time.sleep(0.05)
    last_speed = 0
    arduino.write(bytes(str(int(0)) + '.', 'utf-8'))
    MainWhile=False
    current_speed = 0


arduino = serial.Serial("COM5", 115200)
time.sleep(1)

calibration()
try:

    v = triad_openvr.triad_openvr()
    current_serial, device = slovar_trackers["Человек"]
    z_last = 0
    flag_error = False
    while MainWhile:

        position_device = v.devices[device].sample(1, 500)
        if position_device:
            z = position_device.get_position_z()[0]
            if z == 0.0 and not flag_error:
                z = z_last
                flag_error = True
            elif z == 0.0 and flag_error:
                last_speed = 0
                ExtremeStop()
                print("Stop")
            else:
                z = z - human_0[2]
                current_speed = get_speed(z)
                if abs(current_speed - last_speed) > 30:

                    last_speed = current_speed
                    continue
                arduino.write(bytes(str(int(current_speed)) + '.', 'utf-8'))
                s = bytes(str(int(current_speed)), 'utf-8')
                push(int(current_speed))

                z_last = z
                last_speed = current_speed
except Exception as e:
    print(e)
    ExtremeStop()

