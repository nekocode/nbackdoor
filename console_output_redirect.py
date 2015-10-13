import sys
import win32api
from subprocess import Popen, PIPE

__author__ = 'nekocode'


def main():
    while True:
        cmd_input = raw_input('cmd> ')
        if cmd_input == 'exit':
            break;

        proc = Popen(cmd_input, shell=True, stdout=sys.stdout, stderr=PIPE, stdin=sys.stdin)
        proc.wait()


if __name__ == '__main__':
    main()

