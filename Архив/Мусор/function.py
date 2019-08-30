import serial
import time


def Search(__baudrate=115200):
    __COMlist = []
    __COM = ['COM' + str(i) for i in range(5)]

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
        print(__COMlist)
    return __COMlist


def CheckSerialPortMessage( __baudrate=115200, __timeSleep=5):
    try:
        for __COM in Search():

            port = serial.Serial(__COM, __baudrate)
            time.sleep(__timeSleep)
            large = len(port.readline())
            port.read(large)

            while large > 3:
                for a in range(__timeSleep):

                    date = port.readline().decode().split()

                    if 'treadmill' in date:
                        print(__COM)
                        return __COM

    except Exception as e:
        pass


Search()
CheckSerialPortMessage()
