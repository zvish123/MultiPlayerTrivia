import logging
import socket
import pickle
import inspect
import constants
from protocol import Protocol
import logger


class ClientCommunication:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (constants.SERVER_IP, constants.PORT)
        self.log = None
        self.connect()
        # print(f"connection to server {self.client.getpeername()} is {result}")
        # self.log.write(f"connection to server {self.client.getpeername()} is {result}")

    def connect(self):
        self.client.connect(self.addr)
        log_file_name = f'log/client_{self.client.getsockname()[1]}.log'
        self.log = logger.Logger(log_file_name)
        self.log.write(f"client: {self.client.getsockname()}, connected to server {self.addr}")
        reply = self.client.recv(2048).decode().split()
        # print(f"receive reply:{reply} from {self.client.getpeername()}")
        self.log.write(f"receive reply:{reply} from {self.client.getpeername()}")
        return reply

    # def send(self, data):
    #     try:
    #         self.client.send(data.encode())
    #         print(f"{self.client.getsockname()} send to {self.client.getpeername()}:{data}")
    #
    #         rec = self.client.recv(2048*2)
    #         ret = pickle.loads(rec)
    #         # print(ret)
    #         if data != 'get':
    #             print(f"{self.client.getsockname()} receive from {self.client.getpeername()}: game {str(ret)}")
    #         return ret
    #     except socket.error as e:
    #         print(e)

    def send(self, cmd, params_list, decode=True):
        try:
            data = Protocol.build_message(cmd, params_list)
            self.client.send(data)
            # print(f"{self.client.getsockname()} send to {self.client.getpeername()}: {data.decode()}")
            self.log.write(f"{self.client.getsockname()} send to {self.client.getpeername()}: {data.decode()}")
        except socket.error as e:
            print(e)

    def send_response(self, cmd, params_list, decode=True):
        try:
            data = Protocol.build_message(cmd, params_list)
            self.client.send(data)
            # print(f"{self.client.getsockname()} send to {self.client.getpeername()}: {data.decode()}")
            self.log.write(f"{self.client.getsockname()} send to {self.client.getpeername()}: {data.decode()}")
            rep = self.client.recv(2048)
            if decode:
                rep = rep.decode()
            # print(f"{self.client.getsockname()} receive from {self.client.getpeername()}: {rep}")
            self.log.write(f"{self.client.getsockname()} receive from {self.client.getpeername()}: {rep}")
            return Protocol.parse_message(rep)
            # return rep
        except socket.error as e:
            print(e)

    def receive(self, decode=True):
        try:
            rep = self.client.recv(2048)
            if decode:
                rep = rep.decode()
            # print(f"{self.client.getsockname()} receive from {self.client.getpeername()}: {rep}")
            self.log.write(f"{self.client.getsockname()} receive from {self.client.getpeername()}: {rep}")
            return Protocol.parse_message(rep)
        except socket.error as e:
            print(e)
            return None

    # @staticmethod
    # def who_is_calling_me():
    #     return inspect.stack()[2][3]

    # def __del__(self):
    #     print(f"{self.client.getsockname()} client closing")


if __name__ == "__main__":
    name = input("enter player name:")
