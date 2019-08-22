import serial.tools.list_ports
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import threading
import asyncio
import serial
import time
import sys


class TreadmillControl(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('ui.ui', self)
        self.setWindowTitle('Treadmill controller')
        self.current_speed = 0
        self.speed = 0
        self.acceleration = 0

        self.MainWhile = False
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
        self.DataRecord.toggled.connect(self.record_switch)

    def closeEvent(self, event):
        self.stop()

    def start(self):
        self.MainWhile = True
        main_while_thread = threading.Thread(target=self.main_while)
        main_while_thread.start()
        if self.data_dispatch:
            if self.arduino:
                ard_while_thread = threading.Thread(target=self.ard_while)
                ard_while_thread.start()
            else:
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

                # Отправка данных на ардуину
                print(self.current_speed)
                self.Display.display(self.current_speed)  # Вывод скорости на экран
                time.sleep(0.5)

        self.SpeedBar.setEnabled(True)
        self.AccelerationBar.setEnabled(True)
        self.RightBar.setEnabled(True)
        self.ardControl.setEnabled(True)
        self.StartButton.setEnabled(True)
        return

    def ard_while(self):
        while self.MainWhile:
            x = f"{self.current_speed}."
            self.arduino.write(bytes(x, 'utf-8'))
        return

    def recording_while(self):
        pass

    def stop(self):
        self.MainWhile = False
        self.RecordingWhile = False
        self.SpeedBar.setEnabled(False)
        self.AccelerationBar.setEnabled(False)
        self.SpeedBox.setValue(0)
        self.AccelerationBox.setValue(3)  # Ускорение при остановки
        self.StopButton.setEnabled(False)

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

    def Search(slef, __baudrate=115200):
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



app = QApplication(sys.argv)
ex = TreadmillControl()
ex.show()
sys.exit(app.exec_())

