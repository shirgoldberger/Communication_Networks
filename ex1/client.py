import socket
import sys

from pip._vendor.distlib.compat import raw_input

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    address_from_client = raw_input()
    s.sendto(address_from_client.encode(), (sys.argv[1], int(sys.argv[2])))
    data, addr = s.recvfrom(1024)
    data = data.decode()
    splitData = data.split(",")
    ip = splitData[1]
    print(str(ip))
s.close()