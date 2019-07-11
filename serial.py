import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider, QVBoxLayout, QApplication)
import sys
import glob
import serial

'''from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class SerialThreadClass(QThread):
    rx_signal = pyqtSignal(bytes)
    avaliable_comport_list = ['']
    def __init__(self, port, parent=None):
        super(SerialThreadClass, self).__init__(parent)
        # open the serial port
        self.serport = QSerialPort()
        self.serport.setBaudRate(14400)
        self.serport.setPortName(port)
        self.serport.open(QIODevice.ReadWrite)
    def select_port(self):
        self.my_ports = QSerialPortInfo()
        ports = self.my_ports.availablePorts()
        for port in ports:
            port_name = port.portName()
            SerialThreadClass.avaliable_comport_list.append(port_name)
        print(SerialThreadClass.avaliable_comport_list)
        return SerialThreadClass.avaliable_comport_list
    def run(self):
        while True:
            rx_data = self.serport.readLine()
            if len(rx_data) > 0:
                self.rx_signal.emit(bytes(rx_data))
            self.msleep(5)
    def senddata(self, data):
        tx_data = bytes(data)
        self.serport.write(tx_data)'''


class Sliderdemo(QWidget):
    def __init__(self, vSl=32, parent=None):
        super(Sliderdemo, self).__init__(parent)
        lcd = QLCDNumber(self)
        lcd.display(32)
        vbox = QVBoxLayout()
        sld = QSlider(Qt.Horizontal, self)
        sld.setMinimum(32)
        sld.setTickInterval(1)
        sld.setMaximum(255)
        sld.setValue(vSl)
        sld.setTickPosition(QSlider.TicksBelow)
        sld.setTickInterval(10)
        vbox.addWidget(lcd)
        vbox.addWidget(sld)
        sld.valueChanged[int].connect(self.valuechange)
        self.setLayout(vbox)
        sld.valueChanged.connect(lcd.display)
        self.setWindowTitle("slider")
        #print(self.valuechange())
        print("__init__vSl -> ", vSl)

    def valuechange(self, value):
        #self.size = self.sl.value()
        self.__init__(value)
        #return self.size

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def write_to_port(port,message=""):
    port = serial.Serial(port=str(port), \
                         baudrate=115200, \
                         parity=serial.PARITY_NONE, \
                         stopbits=serial.STOPBITS_ONE, \
                         bytesize=serial.EIGHTBITS, \
                         timeout=0)
    port.write(bytes(message))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Sliderdemo(32)
    ex.show()
    sys.exit(app.exec_())


