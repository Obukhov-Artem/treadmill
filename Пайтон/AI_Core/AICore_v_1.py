#import serial.tools.list_ports
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import triad_openvr
import threading
import serial
import time, csv
import sys
import socket
MAX_DELTA = 150

u = 0
SERIAL = None
UDP_IP = str(socket.gethostbyname(socket.gethostname()))
drag_coefficient = 255
max_speed = 255
UDP_PORT_Rec = 3040
UDP_PORT_Angle = 3040
UDP_PORT_Unity = 3031


class TreadmillControl(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('ui_new.ui', self)
        self.setWindowTitle('Treadmill')
        self.current_speed = 0
        self.treadmill_length = 70
        self.max_speed = 255
        self.human_pos = None
        self.angle = 0

        self.MainWhile = False
        self.ArdWhile = False

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn.bind(('', UDP_PORT_Rec))

        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((UDP_IP, UDP_PORT_Angle))

        # Предустановка Arduino
        try:
            x = self.Search()
            self.COM_port = x[0]
            self.ArdComPort.setText(f'''<p align="center">{x[0]}</p>''')
        except:
            self.COM_port = None

        self.ard_speed = 115200
        self.ard_trackers = 'LHR-9D5EB008'
        self.arduino = None
        if self.arduino:
            try:
                self.ard_connect()
            except:
                pass

        # Калибровка датчиков
        self.calibration()
        self.record_flag = True
        self.speed_unity_k = 1

        # Ui
        self.StartButton.clicked.connect(self.start)
        self.Angle1.clicked.connect(self.angle_1)
        self.Angle2.clicked.connect(self.angle_2)
        self.UP_Button.clicked.connect(self.update_ip)

        self.Calibration_button.clicked.connect(self.calibration)
        self.StopButton.clicked.connect(self.stop)
        self.IP.setText(str(socket.gethostbyname(socket.gethostname())))

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
        self.Ard_trackers_button.clicked.connect(self.ard_change_trackers)
        self.ArdSpeedSelect.clicked.connect(self.ard_change_speed)

        # my checkbox
        self.ActionFlag.clicked.connect(self.type_of_action)
        self.action = 0

    def angle_1(self):
        self.angle = 1
        print("COMMAND1   "+str(int(self.current_speed)) + ',  ' + str(int(self.angle)) + '.')

    def angle_2(self):
        self.angle = 2
        print("COMMAND2   "+str(int(self.current_speed)) + ',  ' + str(int(self.angle)) + '.')

    def calibration(self):
        self.z_napr = 1
        hmd_pos = None
        right_leg, left_leg = None, None
        right_hand, left_hand = None, None
        self.pos_devices_array = []
        try:
            v = triad_openvr.triad_openvr()
            self.human_pos = None
            hmd_pos = None
            self.human_0 = None
            n = 5
            while n > 0 and self.human_pos is None:
                n -= 1
                for device in v.devices:
                    position_device = v.devices[device].sample(1, 500)

                    if position_device:

                        if v.devices[device].device_class == 'HMD':
                            hmd_pos = (position_device.get_position_x()[0], position_device.get_position_y()[0],
                                       position_device.get_position_z()[0],
                                       v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                        else:

                            self.pos_devices_array.append([
                                position_device.get_position_x()[0],
                                 position_device.get_position_y()[0],
                                 position_device.get_position_z()[0],
                                 v.devices[device].get_serial(),
                                 v.device_index_map[v.devices[device].index]])
                            print(v.devices[device].get_serial())
                            if SERIAL is None:
                                print("OK")
                                self.human_0 = [position_device.get_position_x()[0],
                                                position_device.get_position_y()[0],
                                                position_device.get_position_z()[0]]
                                self.human_pos = (v.devices[device].get_serial(),
                                                  v.device_index_map[v.devices[device].index])
                            else:
                                if v.devices[device].get_serial() == SERIAL or v.devices[
                                    device].get_serial() == SERIAL.encode():
                                    print("OK")
                                    self.human_0 = [position_device.get_position_x()[0],
                                                    position_device.get_position_y()[0],
                                                    position_device.get_position_z()[0]]
                                    self.human_pos = (v.devices[device].get_serial(),
                                                      v.device_index_map[v.devices[device].index])



            p_a = sorted(self.pos_devices_array, key=lambda x: x[1])
            [print(p) for p in p_a]
            if len(p_a) > 0:
                print("New postion")
                pos_str = "x= " + str(self.human_0[0])[:3] + " y= " + str(self.human_0[1])[:3] + " z= " + str(
                    self.human_0[2])[:5] + ""
                print(pos_str)
                for i in range(len(p_a)):
                        p_a[i][0]= p_a[i][0]-self.human_0[0]
                        p_a[i][1] = p_a[i][1]-self.human_0[1]
                        p_a[i][2] = p_a[i][2]-self.human_0[2]


            [print(p) for p in p_a]
            if len(p_a) >= 2:
                if p_a[0][1] < 0.5 and p_a[1][1] < 0.5:
                    if p_a[0][0] < p_a[1][0]:
                        left_leg = (p_a[0][3], p_a[0][4])
                        right_leg = (p_a[1][3], p_a[1][4])
                        del (p_a[0])
                        del (p_a[1])
                    else:
                        right_leg = (p_a[0][3], p_a[0][4])
                        left_leg = (p_a[1][3], p_a[1][4])
                        del (p_a[0])
                        del (p_a[1])

            if len(p_a) >= 2:
                if p_a[0][1] < 1 and p_a[1][1] < 1:
                    if p_a[0][0] < p_a[1][0]:
                        left_hand = (p_a[0][3], p_a[0][4])
                        right_hand = (p_a[1][3], p_a[1][4])
                        del (p_a[0])
                        del (p_a[1])
                    else:
                        right_hand = (p_a[0][3], p_a[0][4])
                        left_hand = (p_a[1][3], p_a[1][4])
                        del (p_a[0])
                        del (p_a[1])
            self.slovar_trackers = {"Человек": self.human_pos,
                                "Правая_нога": right_leg,
                                "Левая_нога": left_leg,
                                "Правая_рука": right_hand,
                                "Левая_рука": left_hand
                                }

            print(self.slovar_trackers)

            self.console_output("Калибровка " + pos_str, color="#000000")
            self.ard_trackers = self.human_pos
            self.Ard_trackers.setText(self.ard_trackers[0])
        except Exception as e:
            self.console_output("VR не подключен ", color="#ff0000")

    def closeEvent(self, event):
        print("EXITING")
        if self.arduino != None:
            self.stop()
            self.conn.close()
            print("EXIT")

    def start(self):

        self.calibration_zone = True
        if not self.arduino:
            self.console_output("Соединение с Ардуино не установлено.", color="#f80000")
            print(self.arduino)
            print("Not connection with arduino")
        elif len(self.pos_devices_array) == 0:

            self.console_output("Трекер не найден.", color="#f80000")
            print(self.pos_devices_array)
        else:
            print(self.arduino)

            self.arduino.write(bytes(str("Treadmill") + '.', 'utf-8'))
            time.sleep(0.05)
            answer = self.arduino.readline()
            print(answer)
            attempt = 0
            while attempt < 50:
                attempt += 1
                self.arduino.write(bytes(str("Treadmill") + '.', 'utf-8'))
                time.sleep(0.05)
                answer = self.arduino.readline()
                print(answer)
                a1 = "Speed".encode() in answer
                if a1:
                    break

            if attempt >= 50:
                self.console_output("Проблема с подключение к СОМ. Переподключитесь заново.", color="#f80000")
                self.Connect.setEnabled(True)
                self.Disconnect.setEnabled(False)
                self.arduino = None
            else:
                print("**************************")
                print(self.arduino.readline())
                print("**************************")

                self.console_output("Платформа запущена.", color="#0000f8")
                self.MainWhile = True
                main_while_thread = threading.Thread(target=self.main_while)
                main_while_thread.start()



                self.StartButton.setEnabled(False)
                self.ArduinoBar.setEnabled(False)
                self.Calibration_button.setEnabled(False)
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

    def get_speed_new(self, z):
        max_speed = self.max_speed
        tr_len = self.treadmill_length * (10 ** -2)
        safe_zona = 0.25
        if z < 0:
            zn = -1
        else:
            zn = 1
        z = abs(z)
        if self.moving:
            if z < safe_zona / 2:
                self.moving = False
                return 0
            elif safe_zona / 2 <= z <= safe_zona:
                delta = tr_len - safe_zona
                speed = (z - safe_zona / 2) * max_speed / (delta)
                if 0 < speed < 40:
                    speed = 40
                else:
                    speed = min(90, speed)                         #testing!!!

                return zn * min(max_speed, speed)
            elif safe_zona <= z <= tr_len:

                delta = tr_len - safe_zona
                if z * drag_coefficient <= max_speed:
                    speed = (z - safe_zona / 2) * max_speed / (delta)

                    # print("work zona")
                    return zn * min(max_speed, speed)
                else:

                    # print("far zona speed")
                    return zn * max_speed
            elif z > tr_len:
                # print("far zona")
                return zn * max_speed
            else:
                print("error")
                return 0
        else:
            if z < safe_zona:
                return 0
            elif safe_zona <= z <= tr_len:
                self.moving = True
                delta = tr_len - safe_zona
                if z * drag_coefficient <= max_speed:
                    speed = (z - safe_zona) * max_speed / (delta)
                    if speed < 5:
                        safe_zona = 0

                    # print("work zona")
                    return zn * min(max_speed, speed)
                else:

                    # print("far zona speed")
                    return zn * max_speed
            else:
                print("error")
                return 0

    def get_speed(self, z):
        max_speed = self.max_speed
        tr_len = self.treadmill_length * (10 ** -2)
        safe_zona = 0.15
        if z < 0:
            zn = -1
        else:
            zn = 1
        z = abs(z)
        if z < safe_zona:
            # print("safe zona")
            return 0
        elif safe_zona <= z <= tr_len:
            delta = tr_len - safe_zona
            if z * drag_coefficient <= max_speed:
                speed = (z - safe_zona) * max_speed / (delta)
                if speed < 25:
                    speed = 25

                # print("work zona")
                return zn * min(max_speed, speed)
            else:

                # print("far zona speed")
                return zn * max_speed
        elif z > tr_len:
            # print("far zona")
            return zn * max_speed
        else:
            print("error")
            return 0

    def get_arduino_speed(self):
        answer = self.arduino.readline().decode()
        return answer

    def ExtremeStop(self):  # problem
        try:
            self.arduino.write(bytes(str(int(self.current_speed)) + ',' + str(int(0)) + '.', 'utf-8'))
            self.console_output("Остановка платформы.", color="#f80000")
            print("*" * 10, "Extreme stop", self.current_speed)
            self.MainWhile = False

            if self.current_speed > 0:
                time.sleep(0.1)
                self.arduino.write(bytes(str('Disconnect') + '.', 'utf-8'))
                time.sleep(0.05)
                answer = self.arduino.readline().decode()
                print(answer)
                while self.current_speed > 0 and "Wait" not in answer:
                    if self.arduino:
                        self.current_speed -= 1
                        time.sleep(0.05)
                        self.arduino.write(bytes(str('Disconnect') + '.', 'utf-8'))
                        self.conn.sendto(bytes(str(int(self.current_speed*self.speed_unity_k )).rjust(4, " "), 'utf-8'),
                                         (UDP_IP, UDP_PORT_Unity))
                        m = self.arduino.readline().decode()
                        print(m)
                        if "Speed=" in m:
                            status1, status2 = m.split(",")

                        self.Status_2.setText(
                            '''<p align="center"><span style="color:#2f8700;">''' + status1 + '''</span></p>''')

                        self.Status_3.setText(
                            '''<p align="center"><span style="color:#2f8700;">''' + status2 + '''</span></p>''')

                    else:
                        break

            else:
                time.sleep(0.1)
                self.arduino.write(bytes(str('-Disconnect') + '.', 'utf-8'))
                time.sleep(0.05)
                answer = self.arduino.readline().decode()
                print(answer)
                while self.current_speed < 0 and "Wait" not in answer:
                    if self.arduino:
                        self.current_speed += 1
                        time.sleep(0.05)
                        # print("extreme", self.current_speed)
                        self.arduino.write(bytes(str('-Disconnect') + '.', 'utf-8'))
                        self.conn.sendto(bytes(str(int(self.current_speed*self.speed_unity_k )).rjust(4, " "), 'utf-8'),
                                         (UDP_IP, UDP_PORT_Unity))
                        m = self.arduino.readline().decode()
                        print(m)
                        if "Speed=" in m:
                            status1, status2 = m.split(",")

                        self.Status_2.setText(
                            '''<p align="center"><span style="color:#2f8700;">''' + status1 + '''</span></p>''')

                        self.Status_3.setText(
                            '''<p align="center"><span style="color:#2f8700;">''' + status2 + '''</span></p>''')
                    else:
                        break

            self.last_speed = 0
            # self.arduino.write(bytes(str(int(0)) + '.', 'utf-8'))
            self.current_speed = 0

            self.StartButton.setEnabled(True)
            print("STOP complete")
        except Exception as e:
            print("EXTREME", e, e.__class__)
            print(self.arduino, self.ArdWhile)
        self.console_output("Платформа остановлена", color="#f89000")

    def NormalStop(self):  # problem
        try:
            self.arduino.write(bytes(str(int(self.current_speed)) + ',' + str(int(0)) + '.', 'utf-8'))
            self.console_output("Остановка платформы.", color="#f80000")
            print("*" * 10, "Normal stop", self.current_speed)
            self.MainWhile = False

            if self.current_speed > 0:
                time.sleep(0.1)
                self.arduino.write(bytes(str(int(self.current_speed)) + ',' + str(int(0)) + '.', 'utf-8'))
                time.sleep(0.05)
                while self.current_speed > 0:
                    if self.arduino:
                        self.current_speed -= 3
                        time.sleep(0.05)
                        self.arduino.write(bytes(str(int(self.current_speed)) + ',' + str(int(0)) + '.', 'utf-8'))
                        self.conn.sendto(bytes(str(int(self.current_speed*self.speed_unity_k )).rjust(4, " "), 'utf-8'),
                                         (UDP_IP, UDP_PORT_Unity))
                        m = self.arduino.readline().decode()
                        print(m)
                        if "Speed=" in m:
                            status1, status2 = m.split(",")

                        self.Status_2.setText(
                            '''<p align="center"><span style="color:#2f8700;">''' + status1 + '''</span></p>''')

                        self.Status_3.setText(
                            '''<p align="center"><span style="color:#2f8700;">''' + status2 + '''</span></p>''')

                    else:
                        break

            else:
                time.sleep(0.1)
                self.arduino.write(bytes(str(int(self.current_speed)) + ',' + str(int(0)) + '.', 'utf-8'))
                time.sleep(0.05)
                while self.current_speed < 0:
                    if self.arduino:
                        self.current_speed += 3
                        time.sleep(0.05)
                        # print("extreme", self.current_speed)
                        self.arduino.write(bytes(str(int(self.current_speed)) + ',' + str(int(0)) + '.', 'utf-8'))
                        self.conn.sendto(bytes(str(int(self.current_speed*self.speed_unity_k )).rjust(4, " "), 'utf-8'),
                                         (UDP_IP, UDP_PORT_Unity))
                        m = self.arduino.readline().decode()
                        print(m)
                        if "Speed=" in m:
                            status1, status2 = m.split(",")

                        self.Status_2.setText(
                            '''<p align="center"><span style="color:#2f8700;">''' + status1 + '''</span></p>''')

                        self.Status_3.setText(
                            '''<p align="center"><span style="color:#2f8700;">''' + status2 + '''</span></p>''')
                    else:
                        break

            self.last_speed = 0
            # self.arduino.write(bytes(str(int(0)) + '.', 'utf-8'))
            self.current_speed = 0

            self.MainWhile = True
            print("STOP complete")
        except Exception as e:
            print("NORMAL", e, e.__class__)
            print(self.arduino, self.ArdWhile)
        self.console_output("Платформа остановлена", color="#f89000")

    def update_ip(self):
        global UDP_IP
        UDP_IP = self.IP.toPlainText()
        print("New IP", UDP_IP)

        self.console_output("Установлен IP: " + str(UDP_IP), color="#0000f8")

    def update_speed(self):
        self.speed_unity_k = int(self.Speed_k_unity.toPlainText())
        print("New self.speed_unity_k",  self.speed_unity_k)

        self.console_output("Установлен speed: " + str(self.speed_unity_k), color="#0000f8")

    def get_all_position(self, openvr):
        data_current = []

        for serial in self.slovar_trackers:
            if self.slovar_trackers[serial]:
                try:
                    current_serial, device = self.slovar_trackers[serial]
                    position_device = openvr.devices[device].sample(1, 500)

                    if position_device:
                        c = position_device.get_position()
                        #x,y,z - нужно расширить (delta + акселерометр или гироскоп)
                        data_current.extend([c[0][0], c[1][0], c[2][0]])

                except Exception as e:
                    print(e)
        data_current.extend([self.current_speed])
        return data_current

    def main_while(self):
        self.moving = False
        status1, status2 = "",""
        self.ConsoleOutput.verticalScrollBar()
        self.last_speed = 0
        angle_message = 0
        start_time = time.time()
        start_time2 = time.time()
        self.data_coord = []
        z = 0
        self.current_speed = 0
        try:            # что за исключение??
            v = triad_openvr.triad_openvr()

            current_serial, device = self.ard_trackers
            z_last = 0
            flag_error = False

            while self.MainWhile:
                try:
                    # or self.current_speed != 0
                    position_device = v.devices[device].sample(1, 500)
                    if position_device and self.arduino:
                        z = position_device.get_position_z()[0]
                        if z == 0.0 and not flag_error:
                            start_error = time.time()
                            flag_error = True

                        elif z == 0.0 and flag_error:
                            end_error = time.time() - start_error
                            if end_error>0.2:
                                self.last_speed = 0
                                self.NormalStop()
                                flag_error = False
                                print("Stop")

                        else:
                            z = z - self.human_0[2]
                            self.current_speed = self.get_speed_new(z)
                            if self.record_flag:
                                if time.time() > start_time + 1 / 50:
                                    self.data_coord.append(self.get_all_position(v))
                                    start_time = time.time()

                            if abs(self.current_speed - self.last_speed) > MAX_DELTA:
                                print("ERROR", self.current_speed, self.last_speed,
                                      abs(self.current_speed - self.last_speed))
                                self.current_speed = self.last_speed
                                continue


                            print("COMMAND   "+str(int(self.current_speed)) + ',  ' + str(int(self.angle)) + '.')
                            self.arduino.write(
                                bytes(str(int(self.current_speed)) + ',' + str(int(self.angle)) + '.', 'utf-8'))
                            self.conn.sendto(bytes(str(int(self.current_speed*self.speed_unity_k )).rjust(4, " "), 'utf-8'),
                                             (UDP_IP, UDP_PORT_Unity))
                            z_last = z
                            self.last_speed = self.current_speed

                            m = self.arduino.readline().decode()
                            print(m)
                            if time.time()-start_time2>0.2:
                                print("UPDATE")
                                start_time2 = time.time()
                                if "Speed=" in m:
                                    status1,status2  = m.split(",")


                                self.Status_2.setText(
                                    '''<p align="center"><span style="color:#2f8700;">'''+status1+'''</span></p>''')


                                self.Status_3.setText(
                                    '''<p align="center"><span style="color:#2f8700;">'''+status2+'''</span></p>''')
                            if self.angle != 0:
                                angle_message +=1
                            if angle_message >500:
                                angle_message =0
                                self.angle = 0
                            s = bytes(str(int(self.current_speed)), 'utf-8')
                           

                    self.Display.display(int(self.current_speed))
                except ZeroDivisionError as zero:

                    print("ZERO", zero)
                    print(z, self.current_speed)
                    continue
            if self.arduino:
                data = self.arduino.readline().decode().split()

            if 'treadmill' in data:
                self.MainWhile = True

            self.MaxSpeedBar.setEnabled(True)
            self.LengthBar.setEnabled(True)
            self.ArduinoBar.setEnabled(True)
            self.StartButton.setEnabled(True)

        except Exception as e:
            print("MAIN EXCEPTION", e, e.__class__)
            print(self.arduino, self.ArdWhile)
            self.MainWhile = False
            self.last_speed = 0
            self.current_speed = 0

            self.StartButton.setEnabled(True)
            if self.arduino:
                self.ExtremeStop()
            # return
        return


    ##################
    def type_of_action(self):
        if self.ActionFlag.isChecked():
            self.action = 1
        else:
            self.action = 0
        print(self.action)
    ###############

    """
    def angle_while(self):
        if self.AngleBox.isChecked():
            print("Control angle")
            while True:
                self.server.settimeout(1)
                try:
                    d = self.server.recvfrom(1024)
                except socket.timeout:
                    print('Time is out. {0} seconds have passed'.format(1))
                    break
                received = d[0]
                new_angle = int(received)
                addr = d[1]
                print('Received data: ', received)
                if new_angle !=  self.angle:
                    self.angle = new_angle
                    self.arduino.write(bytes(str(int(self.current_speed)) + '.', 'utf-8'))
                print('From: ', addr)
            self.server.close()
            return
    """

    def stop(self):
        if self.arduino:
            self.ExtremeStop()
        if self.record_flag:
            print("WRITING")
            name = "data" + datetime.strftime(datetime.now(), "%Hh%Mm%Ss")
            self.csv_writer(f'{name}.csv', self.data_coord)
            self.data_coord = []
            print("WRITING END")
        self.StopButton.setEnabled(False)
        self.ArduinoBar.setEnabled(True)
        self.Calibration_button.setEnabled(True)

    def ard_connect(self):
        try:
            self.arduino = serial.Serial(self.COM_port, self.ard_speed, timeout=0)
            self.arduino.write(bytes('0.', 'utf-8'))
            self.Status.setText('''<p align="center"><span style="color:#2f8700;">Подключено</span></p>''')
            self.Connect.setEnabled(False)
            self.Disconnect.setEnabled(True)
            self.console_output("Соединение с Ардуино установлено.", color="#2f8700")

        except Exception as e:
            if self.COM_port:
                self.console_output("Соединение с Ардуино не установлено. Проверьте COM-порт или скорость.",
                                    color="#f80000")
            else:
                self.console_output("COM-порт не выбран.", color="#f80000")
            print(e)

    def Search(self, __baudrate=115200):
        __COMlist = []
        __COM = ['COM' + str(i) for i in range(2, 100)]

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

    def ard_change_trackers(self):
        global SERIAL
        accept_trackers = []
        for device in self.pos_devices_array:
            accept_trackers.append(device[3])
        tracker, ok = QInputDialog.getItem(self, "Трекеры", "Доступные трекеры", accept_trackers, False)
        if ok:
            for device in self.pos_devices_array:
                if device[3] == tracker:
                    self.ard_trackers = device
                    self.Ard_trackers.setText(tracker)
                    SERIAL = tracker
                    self.console_output("Выбран трекер " + str(tracker), color="#0000f8")

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
        self.MaxSpeedBox.setEnabled(not self.MaxSpeedBox.isEnabled())
        self.MaxSpeedSlider.setEnabled(not self.MaxSpeedSlider.isEnabled())

        if self.MaxSpeedSlider.isEnabled():
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


    def csv_writer(self, path, data):   # запись в цсв
        with open(path, "w", newline='') as out_file:
            writer = csv.writer(out_file, delimiter=';')
            for row in data:
                writer.writerow(row)


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))

    print(text)
    print(None, 'Error', text)
    quit()


import sys

sys.excepthook = log_uncaught_exceptions    #почему без аргументов????

app = QApplication(sys.argv)
ex = TreadmillControl()
ex.show()
sys.exit(app.exec_())
