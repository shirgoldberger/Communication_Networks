import socket
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(('', int(sys.argv[1])))

server.listen(1)

while True:
    client_socket, client_address = server.accept()
    print('Connection from: ', client_address)
    try:
        client_socket.settimeout(1.0)
        data_byte = client_socket.recv(100)
        if not data_byte:
            continue

        data = data_byte.decode()
        data_array = data.split('\r\n')
        connection = ""
        for x in data_array:
            if x.startswith("Connection:"):
                connection = (x.split(' '))[1]
                break
        file_name = (data_array[0].split(' '))[1]
        if file_name == "/":
            file_name = "/index.html"
        file_name = "files" + file_name
        if file_name.endswith("jpg") or file_name.endswith("ico"):
            file = open(file_name, "rb")
            content = file.read()
            length = len(content)
        else:
            file = open(file_name, "r")
            content = file.read().encode()
            length = len(file.readlines())
        print('Received: ', data)
        if file_name == "files/result.html":
            messege = "HTTP/1.1 301 Moved Permanently\nConnection: close\nLocation: /result.html\n\n".encode() + content
        else:
            messege = ("HTTP/1.1 200 OK\n" + "Connection: " + connection + "\nContent-Length: " + str(length) + "\n\n").encode() + content
        client_socket.send(messege)
        if connection == "close":
            client_socket.close()
            print('Client disconnected')
    except socket.timeout:
        continue
    except IOError:
        client_socket.send(b'HTTP/1.1 404 Not Found\r\nConnection: close\n\n')

