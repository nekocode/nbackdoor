#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from subprocess import Popen, PIPE
import threading
from websocket import create_connection

__author__ = 'nekocode'


class WebscoketOutput(object):
    def __init__(self, websocket):
        self.buff = ''
        self.__console__ = sys.stdout
        # sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        self.websocket = websocket

    def write(self, output_stream):
        self.buff += output_stream
        self.to_console()
        self.to_websocket()

    def to_console(self):
        sys.stdout = self.__console__
        sys.stdout.write(self.buff)

    def to_websocket(self, file_path):
        self.websocket.send(self.buff + '\n')

    def flush(self):
        self.buff = ''


def print_out(proc):
    data = proc.stdout.read(1)
    sys.stdout.write(data)
    sys.stdout.flush()
    while data:
        data = proc.stdout.read(1)
        sys.stdout.write(data)
        sys.stdout.flush()


def print_err(proc):
    data = proc.stderr.read(1)
    sys.stdout.write(data)
    sys.stdout.flush()
    while data:
        data = proc.stderr.read(1)
        sys.stdout.write(data)
        sys.stdout.flush()


class Test(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.daemon = True
        self.start()

    def run(self):
        while True:
            # sys.stdout.write('_')
            char = sys.stdin.read()
            sys.stdout.write(' -' + char + '- ')


def main():
    # ws = create_connection('ws://localhost:8888')

    Test()
    while True:
        line = raw_input('input: ')
        # print line

    while True:
        cmd_input = raw_input('cmd> ')
        if cmd_input == 'exit':
            break
        elif cmd_input == 'cmd':
            print u'已经处于命令行模式'
            continue

        proc = Popen(cmd_input, shell=True, stdout=PIPE, stderr=PIPE, stdin=sys.stdin)

        print_out(proc)
        print_err(proc)
        print

        proc.wait()


if __name__ == '__main__':
    main()
