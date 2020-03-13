
import serial
import time, csv
import sys
import socket

__COMlist = []
__COM = ['COM' + str(i) for i in range(2, 100)]

for _COM in __COM:
    try:
        COMport = (serial.Serial(port=_COM,
                                 baudrate=115200,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS,
                                 timeout=0))
        if COMport:
            __COMlist.append(_COM)
    except Exception as e:
        pass
speeds = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
ard_speed = '115200'
COM_port = "COM2"
arduino = serial.Serial(COM_port, ard_speed, timeout=0)
arduino.write(bytes('0.', 'utf-8'))
value = 1
arduino.write(bytes(str(int(value)) + '.', 'utf-8'))

m = arduino.readline().decode()
print(m)