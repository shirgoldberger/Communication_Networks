import socket
import sys
import datetime


def delete_line_from_file(file_name):
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for l in lines:
            if l.strip("\n") != line:
                f.write(l)


def get_data_from_parent():
    parent_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # ask the parent server
    parent_socket.sendto(data1, (sys.argv[2], int(sys.argv[3])))
    data2, addr2 = parent_socket.recvfrom(1024)
    parent_data_to_client = data2.decode()
    # create new line for file
    new_line = parent_data_to_client + "," + str(datetime.datetime.now().strftime('%b %d %Y %I:%M%p')) + "\n"
    with open(sys.argv[4], 'a') as writeInFile:
        writeInFile.write(new_line)
    parent_socket.close()
    return parent_data_to_client


def handle_with_dynamic_line(array_of_splited_line):
    # this is a dynamic line
    if len(array_of_splited_line) > 3:
        date = datetime.datetime.strptime(array_of_splited_line[3], '%b %d %Y %I:%M%p') + datetime.timedelta(
            seconds=int(array_of_splited_line[2]))
        x = datetime.datetime.now()
        # check the TTL
        if datetime.datetime.now() > date:
            # delete the line from the file
            delete_line_from_file(sys.argv[4])
            return True
    return False


def send_data_to_client(line, s, addr1):
    split_data = line.split(",")
    data_to_client = split_data[0] + "," + split_data[1] + "," + split_data[2]
    s.sendto(data_to_client.encode(), addr1)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', int(sys.argv[1])))

# wait for clients
while True:
    # take data from client
    data1, addr1 = s.recvfrom(1024)
    isFound = False
    # check if the address is in the file
    with open(sys.argv[4], "r") as file:
        for line in file:
            # remove the \n
            line = line.rstrip()
            array = line.split(",")
            if array[0] == data1.decode():
                # if this is a dynamic line then handle it and check about the date
                if handle_with_dynamic_line(array):
                    continue
                # send data to client
                send_data_to_client(line, s, addr1)
                isFound = True
                break
    # call to parent server
    if not isFound:
        # there is no parent server
        if sys.argv[2] == '-1' or sys.argv[3] == '-1':
            continue
        # get data from parent server
        parent_data = get_data_from_parent()
        # send data to client
        send_data_to_client(parent_data, s, addr1)
s.close()