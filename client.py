#      client

import socket
import time
import re

D_HOST = "127.0.0.1"  # The server's hostname or IP address
D_PORT = 11241  # The port used by the server

HOST = input("server ip: ")
PORT = input("server port(just press enter): ")
if PORT.strip() == "":
    PORT = D_PORT

class Client():
    def __init__(self, ip, port):

        self.current_dir = "\\"
        self.server_ip = ip
        self.server_port = port


    def get_data_from_socket(self, bytes_count: int) -> bytes:
        b = b''
        while len(b) < bytes_count:  # Пока не получили нужное количество байт
            part = self.client_sock.recv(bytes_count - len(b))  # Получаем оставшиеся байты
            if not part:  # Если из сокета ничего не пришло, значит его закрыли с другой стороны
                raise IOError("Соединение потеряно")
            b += part
        return b

    def load_bytes_from_file(self, file_path: str) -> bytes:
        byt = b''
        file = open(file_path, "rb")
        byt = file.read()
        return byt


    def send_file(self, input_file_path: str):
        data = self.load_bytes_from_file(input_file_path)
        output_file_path = input_file_path.split('\\')
        output_file_path = self.current_dir + output_file_path[ len(output_file_path) - 1 ]
        print("ofp: " , output_file_path)

        comand = "upload~" + output_file_path + ((512 - len("upload~" + output_file_path)) * ' ')
        self.client_sock.send(bytes( comand , "utf-8"))

        chunk_size = 4096
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            self.client_sock.send(len(chunk).to_bytes(2, "big"))
            self.client_sock.send(chunk)
        self.client_sock.send(b"\x00\x00")


    def download_file(self, path_on_server, path_on_pc):
        comand = "download~" + self.current_dir + path_on_server + ((512 - len("upload~" + self.current_dir + path_on_server)) * ' ')
        self.client_sock.send(bytes(comand, "utf-8"))

        data = b''
        while True:
            part_len = int.from_bytes(self.get_data_from_socket(2), "big")  # Определяем длину ожидаемого куска
            if part_len == 0:  # Если пришёл кусок нулевой длины, то приём окончен
                break
            data += self.get_data_from_socket(part_len)  # Считываем сам кусок

        file = open(path_on_pc, "wb")
        try:
            file.write(data)
        finally:
            file.close()


    def start(self):

        while True:
            input_data = input("input: ")
            input_data = input_data.strip().split(' ')

            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_sock.connect((self.server_ip, self.server_port))
            try:

                match input_data[0]:
                    case "upload":
                        self.send_file(input_data[1])
                    case "download":
                        self.download_file(input_data[1], input_data[2])
                    case "stop":
                        self.client_sock.sendall(bytes("stop", "utf-8"))
            finally:
                self.client_sock.close()


client = Client(HOST, PORT)
client.start()

input("end")