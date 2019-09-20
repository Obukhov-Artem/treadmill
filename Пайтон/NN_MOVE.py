
UDP_IP = "192.168.0.115"
UDP_PORT_Rec = 3040
UDP_PORT_Unity = 3021
import socket

conn = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
conn.bind(('',UDP_PORT_Rec))

conn.sendto(bytes(str(int(self.current_speed)).rjust(4," "), 'utf-8'), (UDP_IP, UDP_PORT_Unity))