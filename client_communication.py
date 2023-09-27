import socket
import constants
from protocol import Protocol
import logger


class ClientCommunication:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (constants.SERVER_IP, constants.PORT)
        self.log = None
        self.connect()
        self.shared_key = None

    def set_shared_key(self, key):
        self.shared_key = key

    def connect(self):
        self.client.connect(self.addr)
        log_file_name = f'log/client_{self.client.getsockname()[1]}.log'
        self.log = logger.Logger(log_file_name)
        self.log.write(f"client: {self.client.getsockname()}, connected to server {self.addr}")
        reply = self.client.recv(2048).decode().split()
        self.log.write(f"receive reply:{reply} from {self.client.getpeername()}")
        return reply

    def send(self, cmd, params_list):
        try:
            data = Protocol.build_message(cmd, params_list, self.shared_key)
            self.client.send(data)
            self.log.write(f"{self.client.getsockname()} send to {self.client.getpeername()}: {data}")
        except socket.error as e:
            print(e)

    def send_response(self, cmd, params_list):
        try:
            data = Protocol.build_message(cmd, params_list, self.shared_key)
            self.client.send(data)
            self.log.write(f"{self.client.getsockname()} send to {self.client.getpeername()}: {data}")
            rep = self.client.recv(2048)
            if self.shared_key is None:
                rep = rep.decode()
            cmd, data = Protocol.parse_message(rep, self.shared_key)
            self.log.write(f"{self.client.getsockname()} receive from {self.client.getpeername()}: {rep}")
            return cmd, data
        except socket.error as e:
            print(e)
            return None, None
        except Exception as e:
            print(e)
            return None, None

    def receive(self):
        try:
            rep = self.client.recv(2048)
            if self.shared_key is None:
                rep = rep.decode()
            self.log.write(f"{self.client.getsockname()} receive from {self.client.getpeername()}: {rep}")
            return Protocol.parse_message(rep, self.shared_key)
        except socket.error as e:
            print(e)
            return None


if __name__ == "__main__":
    name = input("enter player name:")
