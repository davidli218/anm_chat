from client import help_doc
from share.utils.out import ColoredPrint


class AnonymChatClientHome:
    __exit_flag = False

    def __init__(self):
        self.__CMD_SHEET = (
            _Cmd(['help', 'man'], self.__guide, False, '查看帮助页面'),
            _Cmd(['exit', 'quit'], self.__exit, False, '退出AnonymChat'),
            _Cmd([], None, False, ''),
        )

        while not self.__exit_flag:
            ColoredPrint('anonymChat> ', color='green', end='')
            self.__input_parser(input())

    def __input_parser(self, user_input: str):
        """User input parser"""
        if len(user_input) == 0:  # 处理空白输入
            return

        cmd_name = user_input.split()[0]
        cmd_para = user_input.split()[1:]

        cmd = None
        for cmd in self.__CMD_SHEET:
            if cmd_name.lower() in cmd.name:
                break

        if not cmd.name:
            print(f"{cmd_name}: command is not exist")

        elif cmd.has_arg and len(cmd_para):
            print(f"{cmd_name}: Need at least one parameters")
            print(f"input '{cmd_name} -h' to find the usage")

        elif not cmd.has_arg and (len(cmd_para) > 1 or (len(cmd_para) and cmd_para[0] not in ['-h', '--help'])):
            print(f'{cmd_name} does not need parameters')
            print(f"Input '{cmd_name} -h' to find the usage")

        else:
            cmd.target(cmd_para)

    def __guide(self, args: list):
        """AnonymChat Help Page"""
        if not args:
            print('Help:\nFind the detailed usage by [option] [-h, --help]\n')
            print(f"{'Command':24}{'Need Arg':12}{'Description'}")
            for cmd in self.__CMD_SHEET[:-1]:
                print(f"{str(cmd.name).replace(chr(39), ''):24}{str(cmd.has_arg):12}{cmd.doc}")
            print()

        else:
            print(help_doc.guide_help_doc)

    def __exit(self, args: list):
        """Exit AnonymChat"""
        if not args:
            while True:
                choice = input('Do you want to quit AnonymChat(Y/N): ').upper()
                if choice == 'Y':
                    self.__exit_flag = True
                    return
                if choice == 'N':
                    return
                print("Invalid input, only 'Y' and 'N' is available)")

        else:
            print(help_doc.exit_help_doc)


class _Cmd:
    def __init__(self, name: [str], target, has_arg: bool, doc: str):
        self.name = name  # 名称
        self.target = target  # 调用目标
        self.has_arg = has_arg  # 是否需要参数
        self.doc = doc  # 功能描述
