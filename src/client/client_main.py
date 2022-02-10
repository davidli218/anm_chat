from client import conf, discoverer, home
from share.art import ascii_art_title_4client
from share.utils.out import ColoredPrint
from share.utils.system import clear_screen


class AnonymChatClient:

    def __init__(self):
        self.__client_config = conf.ClientConfig()

    def start(self):
        self.__client_start_ui()

        # 获取服务器通信端口
        discoverer.ConnServer(self.__client_config)

        # CLI
        home.AnonymChatClientHome()

    @staticmethod
    def __client_start_ui():
        """ Initialize client """
        clear_screen()
        ColoredPrint(ascii_art_title_4client, 'yellow')
