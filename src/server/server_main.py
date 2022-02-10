import socket

from server import conf, reception
from share.art import ascii_art_title_4server
from share.utils.out import ColoredPrint
from share.utils.system import clear_screen


class AnonymChatServer:

    def __init__(self, config=conf.DefaultConfig):
        self._G_BROADCAST_PORT = config.G_BROADCAST_PORT  # <服务器> 广播配对信息 </端口>
        self._G_PAIRING_PORT = config.G_PAIRING_PORT  # <服务器> 接受连接请求 </端口>
        self._G_CLIENT_PAIRING_PORT = config.G_CLIENT_PAIRING_PORT  # <客户端> 发现并连接服务器 </端口>
        self._G_MASSAGE_PORT = config.G_MASSAGE_PORT  # <服务器> 稳定通讯 </端口>

    def start(self):
        self._server_start_ui()

        ''' Server Logic '''
        reception_service = reception.ReceptionService(self._G_BROADCAST_PORT, self._G_CLIENT_PAIRING_PORT,
                                                       self._G_PAIRING_PORT, self._G_MASSAGE_PORT)
        reception_service.start()

        input()  # Purse

        ''' Shutdown server '''
        ColoredPrint('=' * 32 + 'System is shutting down' + '=' * 32, 'red')
        reception_service.close()

    def _server_start_ui(self):
        """ Starting Interface """
        clear_screen()
        ColoredPrint(ascii_art_title_4server, 'green')
        ColoredPrint(f'Host name:{socket.gethostname()}\t'
                     f'Host IP:{socket.gethostbyname(socket.gethostname())}\t'
                     f'Pairing by port: {self._G_PAIRING_PORT}', 'cyan')
        print()
