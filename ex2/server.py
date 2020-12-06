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
TWO_LINES = "\r\n\r\n"
ONE_LINE = "\r\n"


def reset_socket(client_socket):
    client_socket.close()
    print('Client disconnected')


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
    while True:
        client_socket, client_address = server_socket.accept()
        print('Connection from: ', client_address)
        client_socket.settimeout(1.0)
        data = ""
        while True:
            try:
                data_byte = client_socket.recv(100)
                if not data_byte:
                    if data == "":
                        reset_socket(client_socket)
                        break
                else:
                    data += data_byte.decode()
                if TWO_LINES not in data:
                    continue
                index = data.find(TWO_LINES)
                if index == -1:
                    continue
                real_data = data[0:index]
                data = data[(index + 4):]
                print('Received: ', data_byte.decode())
                if real_data == "":
                    reset_socket(client_socket)
                    break
                data_array = real_data.split(ONE_LINE)
                # save status connection
                connection = take_status_connection(data_array)
                if connection == "":
                    reset_socket(client_socket)
                    break
                file_name = (data_array[0].split(' '))[1]
                file_name = check_file_name(file_name)
                print(f'file name: {file_name}')
                # the file does not exist
                if not os.path.isfile(file_name):
                    client_socket.send(MESSAGE404.encode())
                    if connection == "close":
                        reset_socket(client_socket)
                        break
                    else:
                        continue
                # the file is an image or an icon
                if file_name.endswith(("jpg", "ico")):
                    with open(file_name, "rb") as file:
                        content = file.read()
                        length = os.stat(file_name).st_size
                        message = (MESSAGE200 + CONNECTION + connection + ONE_LINE + LEN + str(
                            length) + TWO_LINES).encode()
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
                    reset_socket(client_socket)
                    break
            except socket.timeout:
                print("timeout")
                reset_socket(client_socket)
                break
            except IndexError:
                print("index error")
                reset_socket(client_socket)
                break


if __name__ == '__main__':
    main()
