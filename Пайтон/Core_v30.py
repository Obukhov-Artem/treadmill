import serial.tools.list_ports
from datetime import datetime
import triad_openvr
import threading
import serial
import time
import sys
import socket
from flask import Flask, jsonify,request

SERIAL = None
UDP_IP = str(socket.gethostbyname(socket.gethostname()))
drag_coefficient = 255
max_speed = 255
UDP_PORT_Rec = 3040
UDP_PORT_Unity = 3031


class Treadmill():

    def __init__(self):
        self.current_speed = 0
        self.treadmill_length = 70
        self.max_speed = 255
        self.human_pos = None
        self.ard_trackers = 'LHR-9D5EB008'
        self.arduino = None

    def start_treadmill(self):


        self.MainWhile = False
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print(self.conn)
        self.conn.bind(('', UDP_PORT_Rec))

        # Предустановка Arduino
        try:
            x = self.Search()
        except:
            self.COM_port = None
            self.arduino = None

        self.ard_speed = 115200
        if self.arduino:
            try:
                self.ard_connect()
            except:
                pass
        print(self.arduino,self.COM_port)
        # Калибровка датчиков
        self.calibration()
        self.start()

    def calibration(self):
        self.z_napr = 1
        self.human_pos = None
        hmd_pos = None
        self.human_0 = None
        self.pos_devices_array = []
        try:
            v = triad_openvr.triad_openvr()
        except Exception:
            return
        n = 1
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

                        self.pos_devices_array.append(
                            ( v.devices[device].get_serial(),
                             v.device_index_map[v.devices[device].index]))
                        print(v.devices[device].get_serial())
                        if SERIAL is None:
                            print("OK")
                            self.human_0 = [position_device.get_position_x()[0], position_device.get_position_y()[0],
                                            position_device.get_position_z()[0]]
                            self.human_pos = (v.devices[device].get_serial(),
                                              v.device_index_map[v.devices[device].index])
                        else:
                            if v.devices[device].get_serial() == SERIAL or v.devices[device].get_serial() == SERIAL.encode():
                                print("OK")
                                self.human_0 = [position_device.get_position_x()[0],
                                                position_device.get_position_y()[0],
                                                position_device.get_position_z()[0]]
                                self.human_pos = (v.devices[device].get_serial(),
                                                  v.device_index_map[v.devices[device].index])


        p_a = sorted(self.pos_devices_array, key=lambda x: x[1])
        print(p_a)
        if len(p_a)>0:
            print("New position")
            pos_str = "x= "+str(self.human_0[0])[:3]+" y= "+str(self.human_0[1])[:3]+" z= "+str(self.human_0[2])[:5]+""
            print(pos_str)
            self.slovar_trackers = {"Человек": self.human_pos}
            self.ard_trackers = self.human_pos


    def closeEvent(self, event):
        print("EXITING")
        if self.arduino != None:
            self.stop()
            self.conn.close()
            print("EXIT")

    def start(self):
        time.sleep(0.2)

        self.calibration_zone = True
        if not self.arduino:
            print(self.arduino)
            print("Not connection with arduino")
        else:
            n =0
            while n < 15:
                self.arduino.write(bytes(str("Treadmill") + '.', 'utf-8'))
                time.sleep(0.1)
                n += 1
                answer = self.arduino.readline()
                print(answer)
                a1 = "Speed".encode() in answer
                print(a1)
                if a1:
                    break

            print("Платформа запущена.")
            self.MainWhile = True
            main_while_thread = threading.Thread(target=self.main_while)
            main_while_thread.start()

    def get_data(self):
        return {"speed":self.current_speed, "z":self.z}

    def get_speed(self, z):
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
            elif safe_zona/2 <= z <= safe_zona:
                delta = tr_len - safe_zona
                speed = (z - safe_zona/2) * max_speed / (delta)
                if 0<speed <40:
                    speed = 40

                # print("work zona")
                return zn * min(max_speed, speed)
            elif safe_zona <= z <= tr_len:

                delta = tr_len - safe_zona
                if z * drag_coefficient <= max_speed:
                    speed = (z - safe_zona/2) * max_speed / (delta)



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


    def get_arduino_speed(self):
        answer = self.arduino.readline().decode()
        return answer

    def ExtremeStop(self):  # problem
        try:

            print("Остановка платформы.")
            print("*" * 10, "Extreme stop", self.current_speed)
            self.MainWhile = False

            if self.current_speed > 0:
                self.arduino.write(bytes(str('Disconnect') + '.', 'utf-8'))
                while self.current_speed > 0:
                    if self.arduino:
                        self.current_speed -= 1
                        self.arduino.write(bytes(str('Disconnect') + '.', 'utf-8'))
                        answer = self.get_arduino_speed()
                        print(answer)
                    else:
                        break

            else:
                self.arduino.write(bytes(str('-Disconnect') + '.', 'utf-8'))
                while self.current_speed < 0:
                    if self.arduino:
                        self.current_speed += 1
                        print("extreme", self.current_speed)
                        self.arduino.write(bytes(str('-Disconnect') + '.', 'utf-8'))
                        answer = self.get_arduino_speed()
                        print(answer)
                    else:
                        break

            self.last_speed = 0
            self.current_speed = 0

            print("STOP complete")

            print("Платформа остановлена")
        except Exception as e:
            print("EXTREME", e, e.__class__)

    def update_ip(self, ip):
        global UDP_IP
        UDP_IP = ip

    def main_while(self):
        self.moving = False
        self.last_speed = 0
        z = 0
        self.current_speed = 0
        #try:
        v = triad_openvr.triad_openvr()

        current_serial, device = self.ard_trackers
        z_last = 0
        flag_error = False

        while self.MainWhile and self.arduino:
               # try:
                position_device = v.devices[device].sample(1, 500)
                if position_device:
                    z = position_device.get_position_z()[0]
                    self.z = z
                    if z == 0.0 and not flag_error:
                        z = z_last
                        flag_error = True

                    elif z == 0.0 and flag_error:
                        self.last_speed = 0
                        #self.ExtremeStop()
                        print("Stop")

                    else:
                        z = z - self.human_0[2]
                        self.current_speed = self.get_speed(z)

                        if abs(self.current_speed - self.last_speed) > 150:
                            print("ERROR",self.current_speed,self.last_speed, abs(self.current_speed - self.last_speed))
                            self.current_speed = self.last_speed
                            continue
                        if self.arduino:
                            self.arduino.write(bytes(str(int(self.current_speed)) + '.', 'utf-8'))
                        print("ARDUINO", self.arduino.readline())
                        s = bytes(str(int(self.current_speed)), 'utf-8')
                        self.conn.sendto(bytes(str(int(self.current_speed)).rjust(4, " "), 'utf-8'),
                                         (UDP_IP, UDP_PORT_Unity))
                        z_last = z
                        self.last_speed = self.current_speed
                        print(z, self.current_speed)
                        print()
                        """ except ZeroDivisionError as zero:

                    print("ZERO", zero)
                    continue"""
        data = self.arduino.readline().decode().split()

        if 'treadmill' in data:
            self.MainWhile = True
        return
        """
        except Exception as e:
            print("MAIN EXCEPTION", e, e.__class__)
            self.MainWhile = False
            self.last_speed = 0
            self.current_speed = 0

            if self.arduino:
                self.ExtremeStop()
            return"""



    def stop(self):
        if self.arduino:
            self.ExtremeStop()


    def ard_connect(self):
        try:
            self.arduino = serial.Serial(self.COM_port, self.ard_speed)
            self.arduino.write(bytes('0.', 'utf-8'))

        except Exception as e:
            if self.COM_port:
                print("Соединение с Ардуино не установлено. Проверьте COM-порт или скорость.")
            else:
                print("COM-порт не выбран.")
            print(e)

    def Search(self, __baudrate=115200):
        __COMlist = []
        __COM = ['COM' + str(i) for i in range(1, 100)]
        for _COM in __COM:
            try:
                COMport = (serial.Serial(port=_COM,
                                         baudrate=__baudrate,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE,
                                         bytesize=serial.EIGHTBITS,
                                         timeout=0))
                if COMport:
                    __COMlist.append([_COM,COMport])

            except Exception as e:
                pass
        while not self.arduino:
            for com, arduino in __COMlist:
                n = 0
                while n<15:
                    n +=1
                    arduino.write(bytes(str("Treadmill") + '.', 'utf-8'))
                    time.sleep(0.1)
                    answer = arduino.readline()
                    print(answer)
                    a1 = "Speed".encode() in answer
                    print(com,a1)
                    if a1:
                        self.arduino = arduino
                        self.COM_port = com
                        return




    def ard_disconnect(self):
        self.arduino = None


    def set_tracker(self, serial_name):
        global SERIAL
        accept_trackers = []
        for device in self.pos_devices_array:
            accept_trackers.append(device[0])
        for device in self.pos_devices_array:
            if device[0] == serial_name:
                self.ard_trackers = device
                SERIAL = serial_name
                print("Выбран трекер " + str(serial_name))

    """

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
"""



app = Flask(__name__)
TR = Treadmill()


@app.route('/angle', methods=['GET'])
def angle():
    return jsonify({'success': 'default', 'interface_param': None})


@app.route('/start', methods=['GET'])
def start():
    try:
        TR.start_treadmill()
        return jsonify({'start': 'OK'})
    except Exception:
        return jsonify({'start': 'ERROR'})

@app.route('/stop', methods=['GET'])
def stop():
    try:
        TR.stop()
        return jsonify({'stop': 'OK'})
    except Exception:
        return jsonify({'stop': 'ERROR'})

@app.route('/speed', methods=['GET'])
def speed():
    try:
        data = TR.get_data()
        return jsonify(data)
    except Exception:
        return jsonify({'data': 'ERROR'})


@app.route('/adapt',  methods=['POST'])
def set_user_param():
    user_param = ["role","sex","age","education","exp","w_screen","h_screen","hw_type","browser","lang","cpu","lan","gpu"]
    if not request.json:
        return jsonify({'error': 'пустой запрос'})
    elif not all(key in request.json['data'] for key in user_param):
        return jsonify({'error': 'неправильный запрос'})
    user_data = []
    for i in user_param:
        if i == 'browser':
            a = request.json['data'][i]
            if a.lower() in 'safari  firefox  chrome  opera, microsoft explorer': # нужен словарь браузеров на какой-то стороне
                user_data.append(1)
            else:
                user_data.append(6)
        elif i == 'lan':
            a = request.json['data'][i]
            user_data.append(int(float(a.split(".")[0])/1024))
        else:
            user_data.append(int(request.json['data'][i]))
    print(user_data)

    return jsonify({'success': 'OK'})


if __name__ == '__main__':
    app.run(debug=True, port=8001)
