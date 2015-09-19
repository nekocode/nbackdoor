#!/usr/bin/env python
# coding:utf-8
import os
import ctypes
import chardet
__author__ = 'nekocode'


def hide_cmd():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)


def dialog(content, title=u''):
    ctypes.windll.user32.MessageBoxW(None, content, title, 0)


def cmd(cl):
    rlt = os.popen(cl)
    content = ''.join(rlt.readlines())
    return content.decode(chardet.detect(content)['encoding'])


if __name__ == '__main__':
    dialog(cmd('pause'))
