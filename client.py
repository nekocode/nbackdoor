import time
import ctypes
__author__ = 'nekocode'

def hide_cmd():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)

if __name__ == '__main__':
    while True:
        time.sleep(10)
