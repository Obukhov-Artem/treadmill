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

u = 0
RATE = 500
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

    def closeEvent(self, event):
        self.stop()

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

    def get_speed(self, z,r):
        k1 = drag_coefficient / math.e
        max_speed = 255
        safe_zona = 0.15
        tr_len = 0.7
        flag_death = False
        if r<0:
            flag_death = True
        if z>safe_zona:
            flag_death = False
        if z<0:
            zn = -1
        else:
            zn = 1
        z = abs(z)
        """
        if z< safe_zona and not flag_death:
            return 0
        elif z<safe_zona and flag_death:
            delta = tr_len - safe_zona
            speed = (z-safe_zona)*max_speed/(delta)
            return  zn*min(max_speed, speed)
        """
        if z< safe_zona:
            return 0

        elif safe_zona <= z <= tr_len:
            delta = tr_len - safe_zona
            if z * drag_coefficient <= max_speed:
                if r>0:
                    speed = (z-safe_zona)*max_speed/(delta)
                else:
                    speed = (z-safe_zona)*max_speed/(delta)
                return  zn*min(max_speed, speed)
        else:
            return zn*max_speed


    def main_while(self):
        self.ConsoleOutput.verticalScrollBar()
        v = triad_openvr.triad_openvr()
        current_serial, device = self.slovar_trackers["Человек"]
        z_last =0
        data = []
        r =1
        flag_error = False
        flag_stop = False
        while self.MainWhile:

            position_device = v.devices[device].sample(1, 500)
            if position_device:
                z = position_device.get_position_z()[0]*self.z_napr
                print("*"*4,z, self.human_0[2])
                if z == 0.0 and not flag_error:
                    z = z_last
                    flag_error = True
                elif z == 0.0 and flag_error:
                    if not flag_stop:
                        self.arduino.write(bytes(str("d") + '.', 'utf-8'))
                    print("Stop")
                    flag_stop = True

                else:


                    current_speed = self.get_speed(z,r)
                    if len(data)<40:
                        data.append(current_speed)
                    else:
                        r = self.get_r(data)
                        data = data [1:]
                        data.append(current_speed)

                    z = z-self.human_0[2]
                    r = self.get_r(data)
                    #print(z, current_speed)
                    if current_speed:
                        if -drag_coefficient <= current_speed <= drag_coefficient:
                            self.arduino.write(bytes(str(int(current_speed)) + '.', 'utf-8'))
                        else:
                            if current_speed <= -drag_coefficient:
                                z = -1
                            elif current_speed >= drag_coefficient:
                                z = 1
                            time.sleep(1)
                            # self.arduino.write(bytes(str(int(drag_coefficient * z)) + '.'), 'utf-8')
                            x = str(int(drag_coefficient * z)) + '.'

                            self.arduino.write(bytes(str(int(drag_coefficient * z)) + '.', 'utf-8'))
                    z_last = z
            self.Display.display(int(current_speed))
            print(z, current_speed, r)
            print(self.arduino.readline())

            #print(z)
            """
            if -255 <= arr[-1] * 255 <= 255:
                if arr[-1] <= 0:
                    print(arr[-1])
                    '''if int((arr[-1] * acceleration_factor)) > 0:
                        self.arduino.write(bytes(str(int((arr[-1] * drag_coefficient) * 1.1)) + '.',
                                                 'utf-8'))  # Изначально cof = 200
                        self.Display.display(int((arr[-1] * drag_coefficient) * 1.1))'''
                    # else:
                    self.arduino.write(bytes(str(int((arr[-1] * acceleration_factor))) + '.',
                                             'utf-8'))  # Изначально factor = 200
                    self.Display.display(int((arr[-1] * acceleration_factor)))

                    print(int((arr[-1] * acceleration_factor)))
                else:
                    print(arr[-1])
                    if int((arr[-1] * acceleration_factor)) > 0:
                        self.arduino.write(bytes(str(int((arr[-1] * drag_coefficient) * 1.1)) + '.',
                                                 'utf-8'))  # Изначально cof = 200
                        self.Display.display(int((arr[-1] * drag_coefficient) * 1.1))
                    '''else:
                        self.arduino.write(bytes(str(int((arr[-1] * acceleration_factor))) + '.',
                                                 'utf-8'))  # Изначально factor = 200
                        self.Display.display(int((arr[-1] * acceleration_factor)))

                        print(int(abs(arr[-1] * acceleration_factor)))'''

            else:
                print(z)
                x = str(255) + '.'
                time.sleep(1) 
                self.arduino.write(bytes(x), 'utf-8')

                # print(arr[-1])
            """
            '''
            while self.current_speed != self.speed:
                if self.current_speed < self.speed:
                    if self.current_speed + self.acceleration <= self.speed:
                        self.current_speed += self.acceleration
                    else:
                        self.current_speed += 1
                else:
                    if self.current_speed - self.acceleration >= self.speed:
                        self.current_speed -= self.acceleration
                    else:
                        self.current_speed -= 1

                self.Display.display(self.current_speed)  # Вывод скорости на экран

                if self.data_dispatch and self.arduino:
                    x = f"{self.current_speed}."
                    #self.arduino.write(bytes(x), 'utf-8'))
                    self.console_output(self.arduino.readline())
                    # Доделаьть реализовку сокетов
                time.sleep(0.1)'''

        self.arduino.write(bytes('0.', 'utf-8'))
        self.ArdWhile = False
        self.SpeedBar.setEnabled(True)
        self.AccelerationBar.setEnabled(True)
        self.RightBar.setEnabled(True)
        self.ardControl.setEnabled(True)
        self.StartButton.setEnabled(True)
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
                            position_device = v.devices[device].sample(1, RATE)

                            if position_device:
                                c = position_device.get_position()
                                data_current.extend([c[0][0], c[1][0], c[2][0]])

                        except Exception as e:
                            print(e)

                # if self.current_speed != 0:
                #    data_current.append(1)
                # if self.current_speed == 0:
                #    data_current.append(0)
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
                            return __COM

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

    def calibration(self):
        self.z_napr = 1
        v = triad_openvr.triad_openvr()
        right_hand = None
        right_knee = None
        right_leg = None
        left_hand = None
        left_knee = None
        left_leg = None
        human_pos = None
        hmd_pos = None
        self.human_0 = None
        pos_devices_array = []
        n = 1
        while n>0 and human_pos is None:
            n -= 1
            for device in v.devices:
                position_device = v.devices[device].sample(1, 500)

                if position_device:

                    if v.devices[device].device_class == 'HMD':
                        hmd_pos = (position_device.get_position_x()[0], position_device.get_position_y()[0],
                                   position_device.get_position_z()[0],
                                   v.devices[device].get_serial(), v.device_index_map[v.devices[device].index])
                    else:
                        pos_devices_array.append((position_device.get_position_x()[0], position_device.get_position_y()[0],
                                                  position_device.get_position_z()[0],
                                                  v.devices[device].get_serial(),
                                                  v.device_index_map[v.devices[device].index]))
                        print(v.devices[device].get_serial() )
                        if v.devices[device].get_serial() == b'LHR-1761CD18':
                            print("OK")
                            self.human_0 = [position_device.get_position_x()[0], position_device.get_position_y()[0],
                                                  position_device.get_position_z()[0]]
                            human_pos = (v.devices[device].get_serial(),
                                                  v.device_index_map[v.devices[device].index])


            p_a = sorted(pos_devices_array, key=lambda x: x[1])
            print(len(p_a), p_a)
            print(hmd_pos)
            self.z_napr = 1
            """
            for p in p_a:
                if 0.6 < p[1] < 2:
                    if abs(p[0] - hmd_pos[0]) < 0.3:
                        human_pos = (p[3], p[4])
                        if p[2] > 0:
                            self.z_napr = 1
                        else:
                            self.z_napr = -1

            print(self.z_napr, human_pos)
            """
            if len(p_a) > 2:
                if p_a[0][1] < 0.5 and p_a[1][1] < 0.5:
                    if p_a[0][0] < p_a[1][0]:
                        left_leg = (p_a[0][3], p_a[0][4])
                        right_leg = (p_a[1][3], p_a[1][4])
                    else:
                        right_leg = (p_a[0][3], p_a[0][4])
                        left_leg = (p_a[1][3], p_a[1][4])
            if len(p_a) > 4:
                if p_a[2][1] >= 0.5 and p_a[3][1] >= 0.5:
                    if p_a[2][0] < p_a[3][0]:
                        left_leg = (p_a[2][3], p_a[2][4])
                        right_leg = (p_a[3][3], p_a[3][4])
                    else:
                        right_leg = (p_a[2][3], p_a[2][4])
                        left_leg = (p_a[3][3], p_a[3][4])
            if len(p_a) > 6:
                if p_a[4][1] >= 1 and p_a[5][1] >= 1:
                    if p_a[4][0] < p_a[4][0]:
                        left_leg = (p_a[4][3], p_a[4][4])
                        right_leg = (p_a[5][3], p_a[5][4])
                    else:
                        right_leg = (p_a[4][3], p_a[4][4])
                        left_leg = (p_a[5][3], p_a[5][4])

        self.slovar_trackers = {"Человек": human_pos,
                                "Правое_колено": right_knee,
                                "Левое_колено": left_knee,
                                "Правая_голень": right_leg,
                                "Левая_голень": left_leg,
                                "Правая_перчатка": right_hand,
                                "Левая_перчатка": left_hand}

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
