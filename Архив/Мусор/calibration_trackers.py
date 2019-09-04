import serial
import time


def Search(__baudrate=115200, timeSleep=5):

    # Port Database
    __COMlist = []
    __COM = ['COM' + str(i) for i in range(2, 100)]

    for _COM in __COM:
        try:
            COMport = (serial.Serial(port=_COM, \
                                     baudrate=__baudrate, \
                                     parity=serial.PARITY_NONE, \
                                     stopbits=serial.STOPBITS_ONE, \
                                     bytesize=serial.EIGHTBITS, \
                                     timeout=0))

            if COMport:
                # COMlist Creation
                __COMlist.append(_COM)
            else:
                pass

        except Exception as e:
            '''ErrorAttachment = open("SerialErrorAttachment.txt", "a")
            ErrorAttachment.write(e.__class__.__name__ + "\r")
            ErrorAttachment.close()'''
            continue
    return __COMlist


def CheckSerialPortMessage(__activeCOM=Search(), __baudrate=115200, __timeSleep=5):
    try:
        for __COM in __activeCOM:

            port = serial.Serial(__COM, __baudrate)
            time.sleep(__timeSleep)
            large = len(port.readline())
            port.read(large)

            while True:

                if large > 3:
                    for a in range(__timeSleep):

                        date = port.readline().decode().split()

                        if 'treadmill' in date:
                            return __COM

                else:
                    break

    except Exception as e:
        return e


CheckSerialPortMessage()
