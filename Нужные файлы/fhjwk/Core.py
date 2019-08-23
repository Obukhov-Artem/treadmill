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

    def main_while(self):
        self.ConsoleOutput.verticalScrollBar()

        while self.MainWhile:
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

                self.Display.display(self.current_speed) # Вывод скорости на экран
                if self.data_dispatch and self.arduino:
                    x = f"{self.current_speed}."
                    self.arduino.write(bytes(x, 'utf-8'))
                time.sleep(0.1)

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

            if self.current_speed != 0:
                data_current.append(1)
            if self.current_speed == 0:
                data_current.append(0)
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
        v = triad_openvr.triad_openvr()
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
