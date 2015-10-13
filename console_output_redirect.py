import sys
import win32api
from subprocess import Popen, PIPE
__author__ = 'nekocode'


def ctrl_handler(ctrl_type):
    return True


def main():
    win32api.SetConsoleCtrlHandler(ctrl_handler, True)
    while True:
        cmd_input = raw_input('cmd> ')
        proc = Popen(cmd_input, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        # stdout_value = proc.stdout.read()
        # stdout_value += proc.stderr.read()
        sys.stdout = proc.stdout

        # p.stdin.write(cmd_input)


if __name__ == '__main__':
    main()

