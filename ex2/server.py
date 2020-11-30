import socket
import sys
import os.path

MESSAGE404 = "HTTP/1.1 404 Not Found\r\nConnection: close\n\n"
MESSAGE301 = "HTTP/1.1 301 Moved Permanently\nConnection: close\nLocation: /result.html\n\n"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', int(sys.argv[1])))
server.listen(1)

client_socket, client_address = server.accept()
print('Connection from: ', client_address)


while True:
    try:
        client_socket.settimeout(1.0)
        data_byte = client_socket.recv(100)
        if not data_byte:
            client_socket.close()
            continue
        data = data_byte.decode()
        print('Received: ', data)
        if data == "":
            client_socket.close()
            continue
        data_array = data.split('\r\n')
        connection = ""
        for x in data_array:
            if x.startswith("Connection:"):
                connection = (x.split(' '))[1]
                break
        if connection == "":
            continue
        file_name = (data_array[0].split(' '))[1]
        if file_name == "/":
            file_name = "/index.html"
        file_name = "files" + file_name
        if not os.path.isfile(file_name):
            client_socket.send(MESSAGE404.encode())
            if connection == "close":
                client_socket.close()
                print('Client disconnected')
                client_socket, client_address = server.accept()
                print('Connection from: ', client_address)
            continue
        if file_name.endswith(("jpg", "ico")):
            file = open(file_name, "rb")
            content = file.read()
            length = len(content)
            message = ("HTTP/1.1 200 OK\r\n" + "Connection: " + connection + "\r\nContent-Type: "
                       "image/jpeg\r\nContent-Length: " + str(length) + "\r\n\r\n").encode()
        else:
            file = open(file_name, "r")
            content = file.read().encode()
            length = len(content)
            message = ("HTTP/1.1 200 OK\r\n" + "Connection: " + connection + "\r\nContent-Length: "
                       + str(length) + "\r\n\r\n").encode()
        if file_name == "files/result.html":
            message = MESSAGE301.encode()
        message += content
        client_socket.send(message)
        if connection == "close":
            client_socket.close()
            print('Client disconnected')
            client_socket, client_address = server.accept()
            print('Connection from: ', client_address)
    except socket.timeout:
        client_socket.close()
        continue

