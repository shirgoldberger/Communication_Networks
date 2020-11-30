import socket
import sys
import os.path

MESSAGE404 = "HTTP/1.1 404 Not Found\r\nConnection: close\n\n"
MESSAGE301 = "HTTP/1.1 301 Moved Permanently\nConnection: close\nLocation: /result.html\n\n"


def reset_socket(socket):
    socket.close()
    print('Client disconnected')
    socket, client_address = server.accept()
    socket.settimeout(5.0)
    return socket


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', int(sys.argv[1])))
server.listen(1)

client_socket, client_address = server.accept()
client_socket.settimeout(5.0)
print('Connection from: ', client_address)


while True:
    try:
        data_byte = client_socket.recv(300)
        if not data_byte:
            client_socket = reset_socket(client_socket)
            continue
        data = data_byte.decode()
        print('Received: ', data)
        if data == "":
            client_socket = reset_socket(client_socket)
            continue
        data_array = data.split('\r\n')
        connection = ""
        for x in data_array:
            if x.startswith("Connection:"):
                connection = (x.split(' '))[1]
                break
        if connection == "":
            client_socket = reset_socket(client_socket)
            continue
        file_name = (data_array[0].split(' '))[1]
        if file_name == "/":
            file_name = "/index.html"
        file_name = "files" + file_name
        if not os.path.isfile(file_name):
            client_socket.send(MESSAGE404.encode())
            if connection == "close":
                client_socket = reset_socket(client_socket)
            continue
        if file_name.endswith(("jpg", "ico")):
            file = open(file_name, "rb")
            content = file.read()
            length = len(content)
            message = ("HTTP/1.1 200 OK\r\n" + "Connection: " + connection + "\r\nContent-Length: " + str(length) + "\r\n\r\n").encode()
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
            client_socket = reset_socket(client_socket)
        file.close()
    except socket.timeout:
        client_socket = reset_socket(client_socket)
        continue
    except IndexError:
        client_socket = reset_socket(client_socket)
        continue




