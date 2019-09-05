import socket
ip = "192.168.0.121"
UDP_PORT = 3021
conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
conn.connect((ip, UDP_PORT))
current_speed = 0
while True:
    if current_speed>-300:
        current_speed -=1
    s = bytes(str(int(current_speed)), 'utf-8')
    s2 = bytearray(str(int(current_speed)), 'utf-8')
    print(type(s),type(s2), s,s2)
    # выбрать рабочий вариант
    print(conn.send(s))