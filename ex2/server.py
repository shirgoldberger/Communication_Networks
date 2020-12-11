import socket
import sys
import os.path

MESSAGE200 = "HTTP/1.1 200 OK\r\n"
MESSAGE404 = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"
MESSAGE301 = "HTTP/1.1 301 Moved Permanently\r\nConnection: close\r\nLocation: /result.html\r\n\r\n"
INDEX = "/index.html"
REDIRECT = "/redirect"
CONNECTION = "Connection: "
LEN = "Content-Length: "
TWO_LINES = "\r\n\r\n"
ONE_LINE = "\r\n"


def take_file_name(data_array):
    file_name = ""
    for x in data_array:
        if x.startswith("GET"):
            file_name = (x.split(" "))[1]
            break
    return file_name


def check_file_name(file_name):
    if file_name == "/":
        file_name = INDEX
    if file_name != REDIRECT:
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
        client_socket.settimeout(1.0)
        data = ""
        while True:
            try:
                data_byte = client_socket.recv(100)
                if not data_byte:
                    if data == "":
                        client_socket.close()
                        break
                else:
                    print(data_byte.decode())
                    data += data_byte.decode()
                if TWO_LINES not in data:
                    continue
                index = data.find(TWO_LINES)
                if index == -1:
                    continue
                real_data = data[0:index]
                data = data[(index + 4):]
                if real_data == "":
                    client_socket.close()
                    break
                data_array = real_data.split(ONE_LINE)
                # save status connection
                connection = take_status_connection(data_array)
                if connection == "":
                    client_socket.close()
                    break
                file_name = take_file_name(data_array)
                file_name = check_file_name(file_name)
                # the file does not exist
                if not os.path.isfile(file_name) and file_name != REDIRECT:
                    client_socket.send(MESSAGE404.encode())
                    client_socket.close()
                    break
                # the file is an image or an icon
                if file_name == REDIRECT:
                    message = MESSAGE301.encode()
                elif file_name.endswith(("jpg", "ico")):
                    with open(file_name, "rb") as file:
                        content = file.read()
                        length = os.stat(file_name).st_size
                        message = (MESSAGE200 + CONNECTION + connection + ONE_LINE + LEN + str(
                            length) + TWO_LINES).encode()
                        message += content
                else:
                    with open(file_name, "r") as file:
                        content = file.read().encode()
                        length = len(content)
                        message = (MESSAGE200 + CONNECTION + connection + ONE_LINE + LEN
                                   + str(length) + TWO_LINES).encode()
                        message += content
                client_socket.send(message)
                if connection == "close" or file_name == REDIRECT:
                    client_socket.close()
                    break
            except socket.timeout:
                client_socket.close()
                break


if __name__ == '__main__':
    main()