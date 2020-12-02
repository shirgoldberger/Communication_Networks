import socket
import sys
import os.path

MESSAGE200 = "HTTP/1.1 200 OK\r\n"
MESSAGE404 = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"
MESSAGE301 = "HTTP/1.1 301 Moved Permanently\r\nConnection: close\r\nLocation: /result.html\r\n\r\n"
INDEX = "/index.html"
RESULT = "/result.html"
CONNECTION = "Connection: "
LEN = "Content-Length: "


def reset_socket(server_socket, client_socket):
    client_socket.close()
    print('Client disconnected')
    client_socket, client_address = server_socket.accept()
    print('Connection from: ', client_address)
    client_socket.settimeout(1.0)
    return client_socket, ""


def check_file_name(file_name):
    if file_name == "/":
        file_name = INDEX
    if file_name == "/redirect":
        file_name = RESULT
    file_name = "files" + file_name
    return file_name


def take_status_connection(data_array):
    connection = ""
    for x in data_array:
        if x.startswith(CONNECTION):
            connection = (x.split(' '))[1]
            break
    return connection


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(sys.argv[1])))
    server_socket.listen(1)

    client_socket, client_address = server_socket.accept()
    print('Connection from: ', client_address)
    client_socket.settimeout(1.0)
    data = ""

    while True:
        try:
            data_byte = client_socket.recv(300)
            if not data_byte:
                if data == "":
                    client_socket, data = reset_socket(server_socket, client_socket)
                    continue
            else:
                data += data_byte.decode()
            if '\r\n\r\n' not in data:
                continue
            real_data = (data.split('\r\n\r\n'))[0]
            data = (data.split('\r\n\r\n'))[1:]
            print('Received: ', real_data)
            if real_data == "":
                client_socket, data = reset_socket(server_socket, client_socket)
                continue
            data_array = real_data.split('\r\n')
            # save status connection
            connection = take_status_connection(data_array)
            if connection == "":
                client_socket, data = reset_socket(server_socket, client_socket)
                continue
            file_name = (data_array[0].split(' '))[1]
            file_name = check_file_name(file_name)
            # the file does not exist
            if not os.path.isfile(file_name):
                client_socket.send(MESSAGE404.encode())
                if connection == "close":
                    client_socket, data = reset_socket(server_socket, client_socket)
                continue
            # the file is an image or an icon
            if file_name.endswith(("jpg", "ico")):
                with open(file_name, "rb") as file:
                    content = file.read()
                    length = len(content)
                    message = (MESSAGE200 + CONNECTION + connection + "\r\n" + LEN + str(length) + "\r\n\r\n").encode()
            else:
                with open(file_name, "r") as file:
                    content = file.read().encode()
                    length = len(content)
                    message = (MESSAGE200 + CONNECTION + connection + "\r\n" + LEN
                               + str(length) + "\r\n\r\n").encode()
            if file_name == "files/result.html":
                message = MESSAGE301.encode()
            message += content
            client_socket.send(message)
            if connection == "close":
                client_socket, data = reset_socket(server_socket, client_socket)
        except socket.timeout:
            print("timeout")
            client_socket, data = reset_socket(server_socket, client_socket)
            continue
        except IndexError:
            client_socket, data = reset_socket(server_socket, client_socket)
            continue


if __name__ == '__main__':
    main()

