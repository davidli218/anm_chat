import json
import socket
import sys
import threading
import time
from hashlib import md5

from cilent import conf
from share.utils.out import ColoredPrint
from share.utils.validator import valid_ip_port


class ConnServer:
    """ Find & Connect the server """

    __server_ip = None
    __server_broadcast_port = None
    __server_pairing_port = None
    __server_message_port = None

    __meg_from_server = None

    def __init__(self, client_config: conf.ClientConfig):
        self.__client_config = client_config

        self.__nickname = self.__input_nickname()

        self.__pairing_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__pairing_socket.bind(('', client_config.G_PAIRING_PORT))

        self.__main()

        self.__pairing_socket.close()

        if self.__server_message_port is None:
            sys.exit()
        else:
            client_config.G_SERVER_MASSAGE_ADDR = self.__server_msg_addr

    def __main(self):
        """ Main logic of find & Connect the server """

        # Get server address automatically -- {
        thread_find_by_bc = threading.Thread(target=self.__find_by_broadcast)
        thread_find_by_bc.start()

        i = 0  # Beautiful waiting animation
        while thread_find_by_bc.is_alive():
            print(f"\rLooking for the Server {[chr(92), '/', '-'][i]}", end='')
            time.sleep(0.15)
            i = (i + 1) % 3
        print()
        # } --

        # Get server address manually -- {
        if self.__server_ip is None:
            self.__find_by_manual()
        # } --

        # Connect server -- {
        if self.__conn_server():
            ColoredPrint(f'^_^ Connect with server({self.__server_ip}) successfully', 'cyan')
            print(self.__meg_from_server)
        else:
            print("Server doesn't response.")
        # } --

    def __find_by_broadcast(self):
        """ Find the server automatically via UDP broadcast """

        self.__pairing_socket.settimeout(8)
        start_time = time.time()

        try:
            while time.time() - start_time < 8:
                pkg, addr = self.__pairing_socket.recvfrom(1024)  # Blocking

                msg_dict = self.__unpacker(pkg)
                if not msg_dict:
                    continue

                if abs(time.time() - msg_dict['time_stamp']) < 10:  # Check Unix_timestamp
                    self.__server_ip = addr[0]
                    self.__server_broadcast_port = addr[1]
                    self.__server_pairing_port = msg_dict['port']
                    break
        except socket.timeout:
            pass

    def __find_by_manual(self):
        """ Find the server manually via user input address """

        print('No server detected automatically, please connect the server manually')
        while True:
            addr = input('Enter the server address in IP:Port (like 10.20.71.2:9999):')
            if valid_ip_port(addr):
                addr = addr.split(':')
                self.__server_ip = addr[0]
                self.__server_pairing_port = int(addr[1])
                break
            print(f'{addr} is invalid address!')

    def __conn_server(self) -> bool:
        """ Connecting to the server """

        self.__pairing_socket.settimeout(2)

        response_to_server = {'time_stamp': time.time(),
                              'name': self.__nickname,
                              'port': self.__client_config.G_MASSAGE_RECV_PORT,
                              'py_version': sys.version,
                              'sys_platform': sys.platform}

        self.__pairing_socket.sendto(self.__packager(response_to_server), self.__server_pair_addr)  # 发送连接请求

        try:
            i = addr = pkg = 0
            while addr != self.__server_pair_addr and i < 3:
                pkg, addr = self.__pairing_socket.recvfrom(1024)
                if addr[1] == self.__server_broadcast_port:
                    continue
                i += 1
        except ConnectionResetError:  # Wrong server port
            return False
        except socket.timeout:  # 2 second time out
            return False
        if i >= 3:
            return False

        msg_dict = self.__unpacker(pkg)
        if not msg_dict:
            return False

        self.__server_message_port = msg_dict['port']
        self.__meg_from_server = msg_dict['message']
        return True

    @staticmethod
    def __unpacker(pack: bytes) -> dict:
        """Unpacker

        :param: pack: [ md5(JSON(content)) + ';' + JSON(content) ].UTF-8
        :return: Content
        """

        pack = pack.decode('UTF-8').split(';')

        if len(pack) != 2 or pack[0] != md5(pack[1].encode('UTF-8')).hexdigest():
            return {}

        return json.loads(pack[1])

    @staticmethod
    def __packager(content: dict) -> bytes:
        """Packager

        :param: content: Content
        :return: [ md5(JSON(content)) + ';' + JSON(content) ].UTF-8
        """

        content = json.dumps(content)
        content = ';'.join([md5(content.encode('UTF-8')).hexdigest(), content])

        return content.encode('UTF-8')

    @staticmethod
    def __input_nickname() -> str:
        """ Get user nickname """

        while True:
            name = input('Please give yourself a nickname(Up to 12 characters):')
            if len(name) < 13:
                return name
            print('Invalid nickname, please change new one')

    @property
    def __server_pair_addr(self) -> tuple:
        """ Server pairing address """

        return self.__server_ip, self.__server_pairing_port

    @property
    def __server_msg_addr(self) -> tuple:
        """ Server message address """

        return self.__server_ip, self.__server_message_port
