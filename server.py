#              server

import socket
import os

HOST = "127.0.0.1"
PORT = 11241
BACKLOG = 9
DADFOLDER = "files"


class Server:

    def __init__(self, ip, port, backlog, folder):

        self.ip = ip
        self.port = port
        self.backlog = backlog
        self.folder = folder

        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_sock.bind((self.ip, self.port))
        self.serv_sock.listen(self.backlog)

        print("server ready to work")

    def get_data_from_socket(self, bytes_count: int) -> bytes:
        b = b''
        while len(b) < bytes_count:  # Пока не получили нужное количество байт
            part = self.client_sock.recv(bytes_count - len(b))  # Получаем оставшиеся байты
            if not part:  # Если из сокета ничего не пришло, значит его закрыли с другой стороны
                raise IOError("Соединение потеряно")
            b += part
        return b

    def load_bytes_from_file(self, file_path: str) -> bytes:
        file = open("files" + file_path, "rb")
        try:
            byt = file.read()
        except Exception as e:
            print(e)
            return b"\00\00"
        finally:
            file.close()
        return byt

    def load_file_from_client(self, path: str):
        data = b''
        while True:
            part_len = int.from_bytes(self.get_data_from_socket(2), "big")  # Определяем длину ожидаемого куска
            if part_len == 0:  # Если пришёл кусок нулевой длины, то приём окончен
                break
            data += self.get_data_from_socket(part_len)  # Считываем сам кусок

        file = open(self.folder + path, "wb")
        try:
            file.write(data)
        finally:
            file.close()

    def load_file_to_client(self, path: str):
        data = self.load_bytes_from_file(path)

        chunk_size = 4096
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            self.client_sock.send(len(chunk).to_bytes(2, "big"))
            self.client_sock.send(chunk)
        self.client_sock.send(b"\x00\x00")



    def start(self):
        try:
            while True:
                self.client_sock, self.client_ip = self.serv_sock.accept()
                print("connection: ", self.client_ip)

                input_data = self.client_sock.recv(512)

                if not input_data:
                    continue

                input_data = input_data.decode("utf-8").strip().split('~')
                print("input data: ", input_data)

                match input_data[0]:
                    case "upload":
                        self.load_file_from_client(input_data[1])
                    case "download":
                        self.load_file_to_client(input_data[1])
                    case "stop":
                        break
                    case _:
                        continue

        finally:
            self.serv_sock.close()


server = Server(HOST, PORT, BACKLOG, DADFOLDER)
server.start()
