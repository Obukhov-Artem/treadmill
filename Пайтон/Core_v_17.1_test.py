import serial.tools.list_ports
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
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
SERIAL = b'LHR-1761CD18'
drag_coefficient = 255
max_speed = 255

UDP_IP = "192.168.0.115"
UDP_PORT_Rec = 3040
UDP_PORT_Unity = 3021


class TreadmillControl(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('ui2.ui', self)
        self.setWindowTitle('Treadmill')
        self.current_speed = 0
        self.treadmill_length = 70
        self.max_speed = 0

        self.MainWhile = False
        self.ArdWhile = False
        self.calibration_zone = True
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn.bind(('', UDP_PORT_Rec))

        # Предустановка Arduino
        try:
            x = self.Search()
            self.COM_port = x[0]
            self.ArdComPort.setText(f'''<p align="center">{x[0]}</p>''')
        except:
            self.COM_port = None

        self.ard_speed = 115200
        self.arduino = None
        if self.arduino:
            try:
                self.ard_connect()
            except:
                pass

        # Калибровка датчиков
        self.calibration()

        # Ui
        self.StartButton.clicked.connect(self.start)
        self.StopButton.clicked.connect(self.stop)
        #   -- Max Speed bar
        self.MaxSpeedSlider.valueChanged.connect(self.speed_changed_slider)
        self.MaxSpeedBox.valueChanged.connect(self.speed_changed_box)
        self.MaxSpeedSlider.setValue(255)
        self.SpeedLock.clicked.connect(self.speed_lock)
        #   -- Length Bar
        self.LengthSlider.valueChanged.connect(self.length_changed_slider)
        self.LengthBox.valueChanged.connect(self.length_changed_box)
        self.LengthSlider.setValue(70)
        self.LengthLock.clicked.connect(self.length_lock)
        #   -- Ard control
        self.Connect.clicked.connect(self.ard_connect)
        self.Disconnect.clicked.connect(self.ard_disconnect)
        #   -- Ard settings
        self.ArdComPortSelect.clicked.connect(self.ard_change_port)
        self.ArdSpeedSelect.clicked.connect(self.ard_change_speed)
        self.fieldnames = ['x_tracker_1', 'y_tracker_1', 'z_tracker_1',
                           'x_tracker_2', 'y_tracker_2', 'z_tracker_2',
                           'x_tracker_3', 'y_tracker_3', 'z_tracker_3',
                           'data_on_treadmill']

    def calibration(self):
        self.z_napr = 1
        v = triad_openvr.triad_openvr()
        human_pos = None
        hmd_pos = None
        right_leg, left_leg = None, None
        self.human_0 = None
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
                        if v.devices[device].get_serial() == SERIAL:
                            print("OK")
                            self.human_0 = [position_device.get_position_x()[0], position_device.get_position_y()[0],
                                            position_device.get_position_z()[0]]
                            human_pos = (v.devices[device].get_serial(),
                                         v.device_index_map[v.devices[device].index])
                        else:
                            pos_devices_array.append(
                                (position_device.get_position_x()[0], position_device.get_position_y()[0],
                                 position_device.get_position_z()[0],
                                 v.devices[device].get_serial(),
                                 v.device_index_map[v.devices[device].index]))
                            print(v.devices[device].get_serial())



            p_a = sorted(pos_devices_array, key=lambda x: x[1])
            print(p_a)
            if len(p_a) == 2:
                if p_a[0][1] < 0.5 and p_a[1][1] < 0.5:
                    if p_a[0][0] < p_a[1][0]:
                        left_leg = (p_a[0][3], p_a[0][4])
                        right_leg = (p_a[1][3], p_a[1][4])
                    else:
                        right_leg = (p_a[0][3], p_a[0][4])
                        left_leg = (p_a[1][3], p_a[1][4])

        self.slovar_trackers = {"Человек": human_pos,
                                "Правая_голень": right_leg,
                                "Левая_голень": left_leg
                                }

    def get_all_position(self, openvr):
        data_current = []

        for serial in self.slovar_trackers:
            if self.slovar_trackers[serial]:
                try:
                    current_serial, device = self.slovar_trackers[serial]
                    position_device = openvr.devices[device].sample(1, 500)

                    if position_device:
                        c = position_device.get_position()
                        data_current.extend([c[0][0], c[1][0], c[2][0]])

                except Exception as e:
                    print(e)
        data_current.extend([self.current_speed])
        return data_current


    def closeEvent(self, event):
        self.stop()
        self.conn.close()
        print("EXIT")

    def start(self):
        self.MainWhile = True
        self.starttime = time.time()
        main_while_thread = threading.Thread(target=self.main_while)
        main_while_thread.start()
        if not self.arduino:
            self.console_output("Соединение с Ардуино не установлено.", color="#f80000")


        self.arduino.write(bytes(str("Treadmill") + '.', 'utf-8'))
        time.sleep(0.1)
        self.arduino.write(bytes(str("Treadmill") + '.', 'utf-8'))
        time.sleep(0.1)
        self.arduino.write(bytes(str("Treadmill") + '.', 'utf-8'))
        time.sleep(0.1)
        self.arduino.write(bytes(str("Treadmill") + '.', 'utf-8'))
        time.sleep(0.1)
        print("**************************")
        print(self.arduino.readline())
        print("**************************")
        self.StartButton.setEnabled(False)
        self.ArduinoBar.setEnabled(False)
        self.StopButton.setEnabled(True)

    def get_r(self, data):
        current = data[-1]
        last = data[0]
        avg = sum(data) / len(data)
        delta = 10
        if abs(current) < abs(avg) - delta:
            return -1
        else:
            return 1

    def get_speed(self, z):
        max_speed = self.max_speed
        tr_len = self.treadmill_length * (10 ** -2)
        safe_zona = 0.1
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

                delta_speed = abs(zn * min(max_speed, speed)) - abs(self.last_speed)
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



    def get_speed_new(self, z):
        if self.calibration_zone:
            self.tr_len_default = self.treadmill_length * (10 ** -2)
            self.safe_zona_defalt = 0.3
            self.pre_sz, self.pre_tr = self.safe_zona_defalt,self.tr_len_default
            self.calibration_zone = False
        max_speed = self.max_speed
        safe_zona = self.safe_zona_defalt
        tr_len = self.tr_len_default
        if z < 0:
            zn = -1
        else:
            zn = 1
        z = abs(z)
        z_correct = z - self.safe_zona_defalt
        if z_correct < self.safe_zona_defalt:
            new_safe_zona = max(0.01, self.safe_zona_defalt-z_correct)
            new_tr_len = max(0.01, self.tr_len_default-z_correct)
            if new_safe_zona<self.pre_sz:
                self.pre_sz = new_safe_zona
                safe_zona = new_safe_zona
            else:
                safe_zona = self.pre_sz
            if new_tr_len<self.pre_tr:
                self.pre_tr = new_tr_len
                tr_len = new_tr_len
            else:
                tr_len = self.pre_tr
        if z< 0.03 or self.current_speed ==0:
            self.pre_sz, self.pre_tr = self.safe_zona_defalt, self.tr_len_default
            safe_zona = self.safe_zona_defalt
            tr_len = self.tr_len_default
        print("TEST", z,safe_zona,tr_len)
        if z < safe_zona:
            print("safe zona")
            return 0
        elif safe_zona <= z <= tr_len:
            delta = tr_len - safe_zona
            if z * drag_coefficient <= max_speed:
                speed = (z - safe_zona) * max_speed / (delta)


                #delta_speed = abs(zn * min(max_speed, speed)) - abs(self.last_speed)
                #print("*******", delta_speed)
                #if delta_speed < -0.5:
                #    ks = 1.3
                #    print("work zona - TORMOZHENIE")
               # else:
               #     ks = 1

                print("work zona")
                return zn * min(max_speed, speed)
            else:

                print("far zona speed")
                return zn * max_speed
        elif z > tr_len:
            print("far zona")
            return zn * max_speed
        else:
            print("error")
            return 0

    def ExtremeStop(self):  # problem
        print("*" * 10, "Extreme stop", self.current_speed)
        self.MainWhile = False
        try:
            self.arduino.write(bytes(str('Disconnect') + '.', 'utf-8'))
            if self.current_speed > 0:
                while self.current_speed > 0:
                    self.current_speed -= 2
                    print("extreme", self.current_speed)
                    self.arduino.write(bytes(str(int(max(self.current_speed, 0))) + '.', 'utf-8'))
                    print(str(int(max(self.current_speed, 0))) + '.')
                    time.sleep(0.05)

            else:
                while self.current_speed < 0:
                    self.current_speed += 2
                    print("extreme", self.current_speed)
                    self.arduino.write(bytes(str(int(min(self.current_speed, 0))) + '.', 'utf-8'))
                    print(str(int(min(self.current_speed, 0))) + '.')
                    time.sleep(0.05)
        except Exception:
            self.arduino.write(bytes(str(int(0)) + '.', 'utf-8'))



        self.last_speed = 0
        self.arduino.write(bytes(str(int(0)) + '.', 'utf-8'))
        self.current_speed = 0

        self.StartButton.setEnabled(True)

    def main_while(self):
        self.ConsoleOutput.verticalScrollBar()
        self.last_speed = 0
        self.current_speed = 0
        self.record_flag = False
        self.data_coord = []
        #print(self.slovar_trackers)
        try:
            v = triad_openvr.triad_openvr()
            current_serial, device = self.slovar_trackers["Человек"]
            z_last = 0
            flag_error = False

            while self.MainWhile:  # or self.current_speed != 0
                if time.time() > self.starttime + 1 / 50:
                    self.starttime = time.time()
                    position_device = v.devices[device].sample(1, 500)
                    if position_device:
                        z = position_device.get_position_z()[0]
                        if z == 0.0 and not flag_error:
                            z = z_last
                            flag_error = True

                        elif z == 0.0 and flag_error:
                            self.last_speed = 0
                            self.ExtremeStop()
                            print("Stop")

                        else:
                            z = z - self.human_0[2]
                            self.current_speed = self.get_speed_new(z)
                            if self.record_flag:
                                self.data_coord.append(self.get_all_position(v))

                            if abs(self.current_speed - self.last_speed) > 30:
                                print("ERROR", abs(self.current_speed - self.last_speed))
                                self.last_speed = self.current_speed
                                continue

                            print("send_norm", self.current_speed)
                            self.arduino.write(bytes(str(int(self.current_speed)) + '.', 'utf-8'))
                            s = bytes(str(int(self.current_speed)), 'utf-8')
                            self.conn.sendto(bytes(str(int(self.current_speed)).rjust(4, " "), 'utf-8'),
                                             (UDP_IP, UDP_PORT_Unity))
                            z_last = z
                            self.last_speed = self.current_speed
                self.Display.display(int(self.current_speed))

            #data = self.arduino.readline().decode().split()
            #if 'Connection' in data:
             #   self.MainWhile = True
            data = self.arduino.readline().decode().split()

            if 'treadmill' in data:
                self.MainWhile = True
            self.MaxSpeedBar.setEnabled(True)
            self.LengthBar.setEnabled(True)
            self.ArduinoBar.setEnabled(True)
            self.StartButton.setEnabled(True)

        except Exception as e:
            print(e, e.__class__)
            self.MainWhile = False
            self.ExtremeStop()
        return

    def stop(self):
        self.StopButton.setEnabled(False)
        self.ExtremeStop()
        if self.record_flag:
            print("WRITING")
            name = "data" + datetime.strftime(datetime.now(), "%Hh%Mm%Ss")
            self.csv_writer(f'{name}.csv', self.fieldnames, self.data_coord)
            self.data_coord = []
            print("WRITING END")


    def ard_connect(self):
        try:
            self.arduino = serial.Serial(self.COM_port, self.ard_speed)
            self.arduino.write(bytes('0.', 'utf-8'))
            self.Status.setText('''<p align="center"><span style="color:#2f8700;">Подключено</span></p>''')
            self.Connect.setEnabled(False)
            self.Disconnect.setEnabled(True)

        except Exception as e:
            if self.COM_port:
                self.console_output("Соединение с Ардуино не установлено. Проверьте COM-порт или скорость.",
                                    color="#f80000")
            else:
                self.console_output("COM-порт не выбран.", color="#f80000")
            print(e)

    def Search(self, __baudrate=115200):
        __COMlist = []
        __COM = ['COM' + str(i) for i in range(4, 100)]

        for _COM in __COM:
            try:
                COMport = (serial.Serial(port=_COM,
                                         baudrate=__baudrate,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE,
                                         bytesize=serial.EIGHTBITS,
                                         timeout=0))
                if COMport:
                    __COMlist.append(_COM)

            except Exception as e:
                pass
        return __COMlist

    def CheckSerialPortMessage(self, __baudrate=115200, __timeSleep=5):
        try:
            for __COM in self.Search():

                port = serial.Serial(__COM, __baudrate)
                time.sleep(__timeSleep)
                large = len(port.readline())
                port.read(large)

                while large > 3:
                    for a in range(__timeSleep):

                        date = port.readline().decode().split()

                        if 'treadmill' in date:
                            self.arduino = port
                            self.arduino.write("treadmill")

        except Exception as e:
            pass

    def ard_disconnect(self):
        self.arduino = None
        self.Status.setText('''<p align="center"><span style="color:#ff0004;">Отключено</span></p>''')
        self.Connect.setEnabled(True)
        self.Disconnect.setEnabled(False)

    def ard_change_port(self):
        x = self.Search()
        if x:
            new, ok = QInputDialog.getItem(self, "Выберите COM-порт", "Доступные COM-Порты", x, 0, False)
            if ok:
                self.COM_port = new
                self.ArdComPort.setText(f'''<p align="center">{new}</p>''')
        else:
            self.console_output("COM-порты не найдены", color="#fcba03")

    def ard_change_speed(self):
        speeds = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
        x = speeds.index(str(self.ard_speed))
        new, ok = QInputDialog.getItem(self, "Cкорость", "Доступные скорости", speeds, x, False)
        if ok:
            self.ard_speed = int(new)
            self.ArdSpeed.display(new)

    def change_speed(self):
        self.max_speed = self.MaxSpeedSlider.value()

    def change_length(self):
        self.treadmill_length = self.LengthSlider.value()

    def speed_changed_slider(self):
        self.MaxSpeedBox.setValue(self.MaxSpeedSlider.value())
        self.change_speed()

    def speed_changed_box(self):
        self.MaxSpeedSlider.setValue(self.MaxSpeedBox.value())

    def length_changed_slider(self):
        self.LengthBox.setValue(self.LengthSlider.value())
        self.change_length()

    def length_changed_box(self):
        self.LengthSlider.setValue(self.LengthBox.value())

    def speed_lock(self):
        _translate = QCoreApplication.translate
        self.SpeedBox.setEnabled(not self.SpeedBox.isEnabled())
        self.SpeedSlider.setEnabled(not self.SpeedSlider.isEnabled())

        if self.SpeedSlider.isEnabled():
            self.SpeedLock.setText(_translate("Form", "🔓"))
        else:
            self.SpeedLock.setText(_translate("Form", "🔒"))

    def length_lock(self):
        _translate = QCoreApplication.translate
        self.LengthBox.setEnabled(not self.LengthBox.isEnabled())
        self.LengthSlider.setEnabled(not self.LengthSlider.isEnabled())

        if self.LengthSlider.isEnabled():
            self.LengthLock.setText(_translate("Form", "🔓"))
        else:
            self.LengthLock.setText(_translate("Form", "🔒"))

    def console_output(self, info, *, color: str = ""):
        self.ConsoleOutput.append(
            f'''
                <div style="margin: 2px;">
                        <span>[{datetime.strftime(datetime.now(), "%H:%M:%S")}]</span>
                        <span style="color:{color};">  {info}  </span>
                </div>
            ''')
        self.ConsoleOutput.verticalScrollBar().setValue(self.ConsoleOutput.verticalScrollBar().maximum())
        self.ConsoleOutput.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return

    def csv_writer(self, path, fieldnames, data):
        with open(path, "w", newline='') as out_file:
            writer = csv.writer(out_file, delimiter=';')
            writer.writerow(fieldnames)
            for row in data:
                writer.writerow(row)


app = QApplication(sys.argv)
ex = TreadmillControl()
ex.show()
sys.exit(app.exec_())
