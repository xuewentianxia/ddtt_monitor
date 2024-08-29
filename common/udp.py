import socket
from socket import socket as soc


class UdpHelper:

    def __init__(self, host: str, port: str):
        self.udp = soc(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp.settimeout(3)
        self.ip_address = host, port

    def connect(self):
        self.udp.connect(self.ip_address)

    def close(self):
        self.udp.close()

    def send(self, data: str):
        self.udp.send(data.encode('utf-8'))

    def receive(self, buffer_size: int):
        message = ''
        while 1:
            temp = self.udp.recv(buffer_size).decode('utf-8')
            if not temp:
                break
            message += temp

        return message

    def send_to(self, data: str):
        self.udp.sendto(data.encode(encoding='utf-8'), self.ip_address)

    def receive_from(self, buffer_size: int) -> str:
        message = ''
        while 1:
            temp, address = self.udp.recvfrom(buffer_size)
            temp = temp.decode('utf-8')
            print(f'received data: {temp} at address {address}')
            if temp:
                message += temp
            if not temp or '\n' in temp:
                break

        return message

    def bind(self):
        self.udp.bind(self.ip_address)
