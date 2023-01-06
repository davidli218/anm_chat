import socket

from client import conf


class Communication:
    def __init__(self, client_config: conf.ClientConfig):
        self.dest_port = client_config.G_SERVER_MASSAGE_ADDR

        sk4send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sk4send.bind(('', client_config.G_MASSAGE_SEND_PORT))
        sk4recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sk4recv.bind(('', client_config.G_MASSAGE_RECV_PORT))

        ...
