import socket
import os.path
import sys


def get_file_name(firstLine):
    x = len("GET")
    firstLine = firstLine[x:].strip()
    firstLine = firstLine.split("HTTP/1.1")
    if firstLine[0].strip() == '/':
        return "index.html"
    return firstLine[0].strip()


def get_conn(text):
    return text.split('Connection: ')[1].split('\r\n')[0]

def bytes_to_send(file_name):
    if file_name[-4:] == ".jpg" or file_name[-4:] == ".ico":
        with open(file_name, "rb") as f:
            return f.read()
    with open(file_name, "r") as f:
        return f.read().encode()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', int(sys.argv[1])))
server.listen(5)
while True:
    client_socket, client_address = server.accept()
    while True:
        a, b, c, d, data = ("", "", "", "", "")
        try:
            client_socket.settimeout(1)
            d = client_socket.recv(1).decode()
            client_socket.settimeout(None)
            if not d: break
            while True:
                data += a
                a = b
                b = c
                c = d
                client_socket.settimeout(1)
                d = client_socket.recv(1).decode()
                if a + b + c + d == "\r\n\r\n":
                    data += "\r\n\r\n"
                    client_socket.settimeout(None)
                    break
        except socket.error:
            break
        print(data)
        redirect = b"HTTP/1.1 301 Moved Permanently\r\nConnection: close\r\nLocation: /result.html\r\n\r\n"
        file_not_found = b"HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"
        file_name = get_file_name(data.split("\n")[0])
        if file_name == "/redirect":
            client_socket.send(redirect)
            break
        file_name = "files/" + file_name
        if not os.path.isfile(file_name):
            client_socket.send(file_not_found)
            break
        conn_stat = get_conn(data)
        bytes = bytes_to_send(file_name)
        length = len(bytes)
        header = "HTTP/1.1 200 OK\r\nConnection: " + conn_stat + "\r\nContent-Length: " + str(length) + "\r\n\r\n"
        bytes = header.encode() + bytes
        client_socket.send(bytes)
        if conn_stat == "close":
            break
    client_socket.close()
