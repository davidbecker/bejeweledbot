import ctypes

HWND_BOTTOM = 1
HWND_NOTOPMOST = -2
HWND_TOP = 0
HWND_TOPMOST = -1

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_FRAMECHANGED = 0x0020
SWP_SHOWWINDOW = 0x0040

MB_OK = 0x00
MB_OKCANCEL = 0x01
MB_ABORTRETRYIGNORE = 0x02
MB_YESNOCANCEL = 0x03
MB_YESNO = 0x04
MB_RETRYCANCEL = 0x05
MB_CANCELTRYCONTINUE = 0x06

MB_ICONERROR = 0x010
MB_ICONQUESTION = 0x020
MB_ICONWARNING = 0x030
MB_ICONINFORMATION = 0x040


def find_window(title):
    return ctypes.windll.user32.FindWindowW(0, title)


def bring_window_to_top(hwnd):
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                      SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW | SWP_FRAMECHANGED)


def messagebox(message, hwnd=0, title='', flags=MB_OK):
    return ctypes.windll.user32.MessageBoxW(hwnd, message, title, flags)
