import serial.tools.list_ports
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
#version 12.2
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
ip = "192.168.0.115"
UDP_PORT = 3021
drag_coefficient = 255
import socket



class TreadmillControl(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('ui.ui', self)
        self.setWindowTitle('Treadmill controller')
        self.current_speed = 0
        self.speed = 0
        self.acceleration = 0

        self.MainWhile = False
        self.ArdWhile = False
        self.RecordingWhile = False

        #socket Unity
        self.conn = socket.socket()

        self.conn = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.conn.connect((ip , UDP_PORT))
        # Предустановка Arduino
        try:
            x = self.Search()
            self.COM_port = x[0]
            self.ArdComPort.setText(f'''<p align="center">{x[0]}</p>''')
        except:
            self.COM_port = None

        self.ard_speed = 115200
        self.arduino = None
        self.data_dispatch = self.ArdDataDispatch.isChecked

        # Запись данных
        self.training = False
        self.data_record = False
        self.helmet_data = self.HelmetRec.isChecked
        self.L_hand = self.LhandRec.isChecked
        self.L_knee = self.LkneeRec.isChecked
        self.L_shin = self.LshinRec.isChecked
        self.R_hand = self.RhandRec.isChecked
        self.R_knee = self.RkneeRec.isChecked
        self.R_shin = self.RshinRec.isChecked
        self.fieldnames = ['x_tracker_1', 'y_tracker_1', 'z_tracker_1',
                           'x_tracker_2', 'y_tracker_2', 'z_tracker_2',
                           'x_tracker_3', 'y_tracker_3', 'z_tracker_3',
                           'x_tracker_4', 'y_tracker_4', 'z_tracker_4',
                           'data_on_treadmill']
        self.calibration()

        # Ui
        self.StartButton.clicked.connect(self.start)
        self.StopButton.clicked.connect(self.stop)
        #   -- Speed bar
        self.SpeedSlider.valueChanged.connect(self.speed_changed_slider)
        self.SpeedBox.valueChanged.connect(self.speed_changed_box)
        self.SpeedLock.clicked.connect(self.speed_lock)
        #   -- Acceleration Bar
        self.AccelerationSlider.valueChanged.connect(self.acceleration_changed_slider)
        self.AccelerationBox.valueChanged.connect(self.acceleration_changed_box)
        self.AccelerationLock.clicked.connect(self.acceleration_lock)
        #   -- Training
        self.MoveButton.clicked.connect(self.training_switch)
        self.StayButton.clicked.connect(self.training_switch)
        #   -- Ard control
        self.Connect.clicked.connect(self.ard_connect)
        self.Disconnect.clicked.connect(self.ard_disconnect)
        #   -- Ard settings
        self.ArdComPortSelect.clicked.connect(self.ard_change_port)
        self.ArdSpeedSelect.clicked.connect(self.ard_change_speed)
        #   -- Recording
        self.StartRecordButton.clicked.connect(self.start_recording)
        self.StopRecordButton.clicked.connect(self.stop_recording)
        self.DataRecord.toggled.connect(self.record_switch)

    def calibration(self):
        self.z_napr = 1
        v = triad_openvr.triad_openvr()
        human_pos = None
        hmd_pos = None
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
                        pos_devices_array.append(
                            (position_device.get_position_x()[0], position_device.get_position_y()[0],
                             position_device.get_position_z()[0],
                             v.devices[device].get_serial(),
                             v.device_index_map[v.devices[device].index]))
                        print(v.devices[device].get_serial())
                        if v.devices[device].get_serial() == SERIAL:
                            print("OK")
                            self.human_0 = [position_device.get_position_x()[0], position_device.get_position_y()[0],
                                            position_device.get_position_z()[0]]
                            human_pos = (v.devices[device].get_serial(),
                                         v.device_index_map[v.devices[device].index])

            p_a = sorted(pos_devices_array, key=lambda x: x[1])
            print(p_a)
        self.slovar_trackers = {"Человек": human_pos}

    def closeEvent(self, event):
        self.stop()
        self.conn.close()
        print("EXIT")

    def start(self):
        self.MainWhile = True
        main_while_thread = threading.Thread(target=self.main_while)
        main_while_thread.start()
        if not self.arduino:
            self.console_output("Соединение с Ардуино не установлено.", color="#f80000")

        self.StartButton.setEnabled(False)
        self.RightBar.setEnabled(False)
        self.ardControl.setEnabled(False)
        self.StopButton.setEnabled(True)

    def get_r(self,data):
        current = data[-1]
        last = data[0]
        avg = sum(data)/len(data)
        delta = 10
        if abs(current)<abs(avg)- delta:
            return -1
        else:
            return 1

    def get_speed(self, z,r=1):
        max_speed = 255
        safe_zona = 0.2
        tr_len = 1
        if z<0:
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
                speed = (z-safe_zona)*max_speed/(delta)
                print("work zona")
                return  zn*min(max_speed, speed)
            else:

                print("far zona speed")
                return zn*max_speed
        elif z> tr_len:
            print("far zona")
            return zn * max_speed
        else:
            print("error")
            return 0

    def ExtremeStop(self):#problem
        print("*"*10,"Extreme stop", self.current_speed)
        self.arduino.write(bytes(str('d') + '.', 'utf-8'))
        if self.current_speed>=0:
            while self.current_speed>=0:
                self.current_speed -= 1
                print("extreme", self.current_speed)
                self.arduino.write(bytes(str(int(max(self.current_speed,0))) + '.', 'utf-8'))
                print(str(int(max(self.current_speed,0))) + '.')
                time.sleep(0.05)
        else:

            while self.current_speed<=0:
                self.current_speed += 1
                print("extreme", self.current_speed)
                self.arduino.write(bytes(str(int(min(self.current_speed,0))) + '.', 'utf-8'))
                print(str(int(min(self.current_speed,0))) + '.')
                time.sleep(0.05)
        self.last_speed = 0
        self.arduino.write(bytes(str(int(0)) + '.', 'utf-8'))

        self.current_speed = 0



    def main_while(self):
        self.ConsoleOutput.verticalScrollBar()
        self.last_speed =0
        self.current_speed = 0
        try:
            v = triad_openvr.triad_openvr()
            current_serial, device = self.slovar_trackers["Человек"]
            z_last =0
            flag_error = False
            while self.MainWhile:
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
                        self.current_speed = self.get_speed(z)
                        if abs(self.current_speed-self.last_speed)>10:
                            print("ERROR",abs(self.current_speed-self.last_speed))
                            self.last_speed = self.current_speed
                            continue
                        print("send_norm", self.current_speed)
                        self.arduino.write(bytes(str(int(self.current_speed)) + '.', 'utf-8'))
                        s = bytes(str(int(self.current_speed)), 'utf-8')
                        self.conn.send(s)
                        z_last = z
                        self.last_speed = self.current_speed
                self.Display.display(int(self.current_speed))
                print(z, self.current_speed, time.time())


            data = self.arduino.readline().decode().split()
            if 'treadmill' in data:
                self.MainWhile = True




            self.ArdWhile = False
            self.SpeedBar.setEnabled(True)
            self.AccelerationBar.setEnabled(True)
            self.RightBar.setEnabled(True)
            self.ardControl.setEnabled(True)
            self.StartButton.setEnabled(True)
        except Exception as e:
            print(e,e.__class__)
            self.MainWhile = False
            self.ExtremeStop()
        return

    def stop(self):

        self.SpeedBox.setValue(0)
        self.speed = 0
        self.MainWhile = False
        self.RecordingWhile = False
        self.SpeedBar.setEnabled(False)
        self.AccelerationBar.setEnabled(False)
        self.AccelerationBox.setValue(3)  # Ускорение при остановки
        self.StopButton.setEnabled(False)
        self.ExtremeStop()


#неважный код для управления


    def start_recording(self):
        self.RecordingWhile = True
        self.start = time.time()
        recording_while_thread = threading.Thread(target=self.recording_while)
        recording_while_thread.start()

        self.StartRecordButton.setEnabled(False)
        self.StopRecordButton.setEnabled(True)

    def recording_while(self):
        v = triad_openvr.triad_openvr()
        # v.print_discovered_objects()
        n = 0
        data = []
        while self.RecordingWhile:
            if time.time() > self.start + 1 / 25:
                self.start = time.time()
                data_current = []

                for serial in self.slovar_trackers:
                    if self.slovar_trackers[serial]:
                        try:
                            current_serial, device = self.slovar_trackers[serial]
                            position_device = v.devices[device].sample(1, 500)

                            if position_device:
                                c = position_device.get_position()
                                data_current.extend([c[0][0], c[1][0], c[2][0]])

                        except Exception as e:
                            print(e)

                data_current.append(self.current_speed)
                data_current.append(datetime.now())
                data.append(data_current)
                n += 1
                if n >= 100000:
                    name = self.FileName.text() + datetime.strftime(datetime.now(), "%Hh%Mm%Ss")
                    self.csv_writer(f'{name}.csv', self.fieldnames, data)
                    data = []
                    n = 0

        name = self.FileName.text() + datetime.strftime(datetime.now(), "%Hh%Mm%Ss")
        self.csv_writer(f'{name}.csv', self.fieldnames, data)
        self.StartRecordButton.setEnabled(True)
        self.StopRecordButton.setEnabled(False)
        return

    def stop_recording(self):
        self.RecordingWhile = False

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
        __COM = ['COM' + str(i) for i in range(100)]

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
                            self.arduino= port
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
        self.speed = self.SpeedSlider.value()

    def change_acceleration(self):
        self.acceleration = self.AccelerationSlider.value()

    def speed_changed_slider(self):
        self.SpeedBox.setValue(self.SpeedSlider.value())
        self.change_speed()

    def speed_changed_box(self):
        self.SpeedSlider.setValue(self.SpeedBox.value())

    def acceleration_changed_slider(self):
        self.AccelerationBox.setValue(self.AccelerationSlider.value())
        self.change_acceleration()

    def acceleration_changed_box(self):
        self.AccelerationSlider.setValue(self.AccelerationBox.value())

    def speed_lock(self):
        _translate = QCoreApplication.translate
        self.SpeedBox.setEnabled(not self.SpeedBox.isEnabled())
        self.SpeedSlider.setEnabled(not self.SpeedSlider.isEnabled())

        if self.SpeedSlider.isEnabled():
            self.SpeedLock.setText(_translate("Form", "🔓"))
        else:
            self.SpeedLock.setText(_translate("Form", "🔒"))

    def acceleration_lock(self):
        _translate = QCoreApplication.translate
        self.AccelerationBox.setEnabled(not self.AccelerationBox.isEnabled())
        self.AccelerationSlider.setEnabled(not self.AccelerationSlider.isEnabled())

        if self.AccelerationSlider.isEnabled():
            self.AccelerationLock.setText(_translate("Form", "🔓"))
        else:
            self.AccelerationLock.setText(_translate("Form", "🔒"))


    def record_switch(self):
        self.data_record = not self.data_record

    def training_switch(self):
        self.training = not self.training

        if self.training:
            self.MoveButton.setEnabled(False)
            self.StayButton.setEnabled(True)
        else:
            self.MoveButton.setEnabled(True)
            self.StayButton.setEnabled(False)

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


app = QApplication(sys.argv)
ex = TreadmillControl()
ex.show()
sys.exit(app.exec_())
