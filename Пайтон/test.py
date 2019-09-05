import serial
# Import libraies
import socket
import time
UDP_IP = "192.168.0.115"
UDP_PORT_Rec = 3047
UDP_PORT_Unity = 3021

print("Receiving on Port:" + str(UDP_PORT_Rec))
print("Sending to IP:" + UDP_IP + ":" + str(UDP_PORT_Unity))

# Set socket to send udp messages and bind port
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(('',UDP_PORT_Rec));

## Keep sending message from file location
while True:
    data = b"-222"
    print("Received")

    sock.sendto(data, (UDP_IP, UDP_PORT_Unity))
    print("Send")

"""
# Set send IP adress and port


import socket
import time
def push(speed):

    UDP_PORT = 3021
    ip = "192.168.0.115"
    conn = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    print(conn.connect_ex((ip , UDP_PORT)))
    speed = -200
    print(conn.sendto((bytes(str(speed),'utf-8')), (ip, UDP_PORT)))

    conn.close()


"""
