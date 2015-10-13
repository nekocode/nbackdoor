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


class Input(threading.Thread):
    def __init__(self, proc, ):
        threading.Thread.__init__(self)

        self.daemon = True
        self.start()

    def run(self):
        pass


def main():
    ws = create_connection('ws://localhost:8888')

    while True:

        cmd_input = raw_input('cmd> ')
        if cmd_input == 'exit':
            break

        proc = Popen(cmd_input, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        Input(proc)

        data = proc.stdout.read(1)
        sys.stdout.write(data)
        sys.stdout.flush()
        while data:
            data = proc.stdout.read(1)
            sys.stdout.write(data)
            sys.stdout.flush()

        proc.wait()


if __name__ == '__main__':
    main()
