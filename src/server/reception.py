import json
import socket
import sys
import threading
import time
from hashlib import md5

from share.utils.out import ColoredPrint


class ReceptionService:
    __is_shutdown = False

    def __init__(self, broadcast_port, client_pairing_port, pairing_port, massage_port):
        """
        广播服务器信息，处理客户端连接请求

        :param broadcast_port: 服务器广播配对信息的端口
        :param client_pairing_port: 客户端接收配对信息的端口
        :param pairing_port: 负责配对任务的端口
        :param massage_port: 负责消息收发的端口
        """

        self.__my_name = f'[{self.__class__.__name__} at {id(self)}]'
        self.__broadcast_port = broadcast_port
        self.__broadcast_dest_port = client_pairing_port
        self.__pairing_port = pairing_port
        self.__message_port = massage_port

        # init sockets -> broadcast
        self.__broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.__broadcast_socket.bind(('', self.__broadcast_port))

        # init sockets -> pairing
        self.__pairing_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__pairing_socket.bind(('', self.__pairing_port))

        # init threading
        self.__thread_udp_broadcast = threading.Thread(target=self.__udp_broadcast)
        self.__thread_new_user_waiter = threading.Thread(target=self.__new_user_waiter)

        # log
        print(f'SYS:{self.__my_name} Has been created successfully')
        print(f'SYS:{self.__my_name} Broadcast using port: {self.__broadcast_port}')
        print(f'SYS:{self.__my_name} Pairing using port: {self.__pairing_port}')

    def start(self):
        self.__thread_udp_broadcast.start()
        self.__thread_new_user_waiter.start()

        # log
        print(f'SYS:{self.__my_name} UDP broadcast started')
        print(f'SYS:{self.__my_name} Pairing started')

    def close(self):
        self.__is_shutdown = True

        if sys.platform == 'darwin':
            '''
            Linux and Windows are very forgiving about calling shutdown() on a closed socket.
            But on Mac OS X shutdown() only succeeds if the OS thinks that the socket is still open,
            otherwise OS X kills the socket.shutdown() statement with:
                socket.error: [Errno 57] Socket is not connected
            '''
            try:
                self.__broadcast_socket.shutdown(socket.SHUT_RDWR)
                self.__pairing_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        else:
            self.__broadcast_socket.shutdown(socket.SHUT_RDWR)
            self.__pairing_socket.shutdown(socket.SHUT_RDWR)

        self.__broadcast_socket.close()
        self.__pairing_socket.close()

        self.__thread_new_user_waiter.join()
        self.__thread_udp_broadcast.join()

        # log
        print(f'SYS:{self.__my_name} UDP Broadcast stopped')
        print(f'SYS:{self.__my_name} Pairing stopped')
        ColoredPrint(f'SYS:{self.__my_name} Is closed', 'yellow')

    def __udp_broadcast(self):
        """ UDP Broadcast 用于被客户端发现 """

        broadcast_dest = (socket.gethostbyname(socket.gethostname()).rsplit('.', 1)[0] + '.255',
                          self.__broadcast_dest_port)

        while True:
            broadcast_msg = Message4Pairing(
                {'time_stamp': time.time(),  # Unix_timestamp
                 'port': self.__pairing_port}  # 服务器配对端口
            )

            try:
                self.__broadcast_socket.sendto(broadcast_msg.to_bytes(), broadcast_dest)

                for _ in range(6):  # 广播3秒间隔
                    if self.__is_shutdown:
                        return
                    time.sleep(0.5)
            except OSError as e:
                if not self.__is_shutdown:
                    raise OSError(e)

    def __new_user_waiter(self):
        """ Deal with new client connection request """

        while True:
            welcome_message = f'Welcome!'
            pkg: bytes
            addr: tuple

            try:
                pkg, addr = self.__pairing_socket.recvfrom(1024)  # 等待用户连接
            except OSError as e:
                if not self.__is_shutdown:
                    raise OSError(e)
                return

            if not (msg_dict := Message4Pairing(pkg).to_dict()):
                continue

            if abs(time.time() - msg_dict['time_stamp']) < 10:
                response = {'message': welcome_message,
                            'port': self.__message_port}

                self.__pairing_socket.sendto(Message4Pairing(response).to_bytes(), addr)

                ColoredPrint(f'{addr[0]} Joined the server successfully!'
                             f'\tOS:{msg_dict["sys_platform"]}\tPython:{msg_dict["py_version"].split()[0]}', 'green')


class Message4Pairing:

    def __init__(self, data):
        if isinstance(data, bytes):
            try:
                self.__content = self.__unpacker(data)
            except Exception:
                raise ValueError("Can not parse data")
        elif isinstance(data, dict):
            self.__content = data
        else:
            raise ValueError("Can not parse data")

    def to_dict(self) -> dict:
        return self.__content

    def to_bytes(self) -> bytes:
        return self.__packager(self.__content)

    @staticmethod
    def __packager(content: dict) -> bytes:
        """Packager

        :param content: Content
        :return: [ md5(JSON(content)) + ';' + JSON(content) ].UTF-8
        """

        content = json.dumps(content)
        content = ';'.join([md5(content.encode('UTF-8')).hexdigest(), content])

        return content.encode('UTF-8')

    @staticmethod
    def __unpacker(pack: bytes) -> dict:
        """Unpacker

        :param pack: [ md5(JSON(content)) + ';' + JSON(content) ].UTF-8
        :return: Content
        """

        pack = pack.decode('UTF-8').split(';')

        if len(pack) != 2 or pack[0] != md5(pack[1].encode('UTF-8')).hexdigest():
            return {}

        return json.loads(pack[1])
