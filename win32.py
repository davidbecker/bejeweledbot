import ctypes
import ctypes.wintypes
import win32gui
import win32ui
import faulthandler

faulthandler.enable()

HWND_BOTTOM = 1
HWND_NOTOPMOST = -2
HWND_TOP = 0
HWND_TOPMOST = -1

SW_HIDE = 0
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
SW_FORCEMINIMIZE = 11

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

MAX_PATH = 256

PROCESS_TERMINATE = 0x0001
PROCESS_CREATE_THREAD = 0x0002
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_DUP_HANDLE = 0x0040
PROCESS_CREATE_PROCESS = 0x0080
PROCESS_QUERY_INFORMATION = 0x0400

# The coordinates for the left side of the virtual screen
SM_XVIRTUALSCREEN = 76
# The coordinates for the top of the virtual screen
SM_YVIRTUALSCREEN = 77
# The width of the virtual screen, in pixels
SM_CXVIRTUALSCREEN = 78
# The height of the virtual screen, in pixels
SM_CYVIRTUALSCREEN = 79

CF_BITMAP = 2
# Copies the source rectangle directly to the destination rectangle
SRCCOPY = 13369376

DIB_RGB_COLORS = 0x00
DIB_PAL_COLORS = 0x01
DIB_PAL_INDICES = 0x02

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

# https://docs.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapfileheader
# class BITMAPFILEHEADER(ctypes.Structure):
#     _pack_ = 1  # structure field byte alignment
#     _fields_ = [
#         ('bfType', ctypes.wintypes.WORD),  # file type ("BM")
#         ('bfSize', ctypes.wintypes.DWORD),  # file size in bytes
#         ('bfReserved1', ctypes.wintypes.WORD),  # must be zero
#         ('bfReserved2', ctypes.wintypes.WORD),  # must be zero
#         ('bfOffBits', ctypes.wintypes.DWORD),  # byte offset to the pixel array
#     ]


class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1  # structure field byte alignment
    _fields_ = [
        ('bfType', ctypes.c_ushort),  # file type ("BM")
        ('bfSize', ctypes.c_ulong),  # file size in bytes
        ('bfReserved1', ctypes.c_ushort),  # must be zero
        ('bfReserved2', ctypes.c_ushort),  # must be zero
        ('bfOffBits', ctypes.c_ulong),  # byte offset to the pixel array
    ]


# https://docs.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader
class BITMAPINFOHEADER(ctypes.Structure):
    _pack_ = 1  # structure field byte alignment
    _fields_ = [
        ('biSize', ctypes.wintypes.DWORD),
        ('biWidth', ctypes.wintypes.LONG),
        ('biHeight', ctypes.wintypes.LONG),
        ('biPLanes', ctypes.wintypes.WORD),
        ('biBitCount', ctypes.wintypes.WORD),
        ('biCompression', ctypes.wintypes.DWORD),
        ('biSizeImage', ctypes.wintypes.DWORD),
        ('biXPelsPerMeter', ctypes.wintypes.LONG),
        ('biYPelsPerMeter', ctypes.wintypes.LONG),
        ('biClrUsed', ctypes.wintypes.DWORD),
        ('biClrImportant', ctypes.wintypes.DWORD)
    ]


# https://docs.microsoft.com/de-de/windows/win32/api/wingdi/ns-wingdi-rgbquad
class RGBQUAD(ctypes.Structure):
    _pack_ = 1  # structure field byte alignment
    _fields_ = [
        ('rgbBlue', ctypes.wintypes.BYTE),
        ('rgbGreen', ctypes.wintypes.BYTE),
        ('rgbRed', ctypes.wintypes.BYTE),
        ('rgbReserved', ctypes.wintypes.BYTE)
    ]


# https://docs.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfo
class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', ctypes.POINTER(RGBQUAD))
    ]


# https://docs.microsoft.com/de-de/windows/win32/api/winuser/ns-winuser-keybdinput
class KeyboardInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class _InputUnion(ctypes.Union):
    _fields_ = [("ki", KeyboardInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


# https://docs.microsoft.com/de-de/windows/win32/api/winuser/ns-winuser-input
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", _InputUnion)]

    def __init__(self, element):
        if isinstance(element, KeyboardInput):
            element_type = INPUT_KEYBOARD
            union = _InputUnion(ki=element)
        elif isinstance(element, MouseInput):
            element_type = INPUT_MOUSE
            union = _InputUnion(mi=element)
        elif isinstance(element, HardwareInput):
            element_type = INPUT_HARDWARE
            union = _InputUnion(hi=element)
        else:
            raise TypeError("Unknown input type: %r" % element)

        ctypes.Structure.__init__(self, type=element_type, ii=union)


def send_input_item(input_item: Input) -> int:
    """sends a single input item - returns 1 on success"""
    size = ctypes.sizeof(input_item)
    ptr = ctypes.pointer(input_item)
    return send_input(1, ptr, size)


SM_CXSCREEN = 0
SM_CYSCREEN = 1


def convert_window_to_screen_coordinates(x: int, y: int) -> (int, int):
    x_screen = x * 0xFFFF / (get_system_metric(SM_CXSCREEN) - 1)
    y_screen = y * 0xFFFF / (get_system_metric(SM_CYSCREEN) - 1)
    return int(x_screen), int(y_screen)


def is_window(hwnd: ctypes.wintypes.HWND) -> bool:
    """https://docs.microsoft.com/de-de/windows/win32/api/winuser/nf-winuser-iswindow?redirectedfrom=MSDN"""
    IsWindow = ctypes.windll.user32.IsWindow
    IsWindow.argtypes = [ctypes.wintypes.HWND]
    IsWindow.restype = ctypes.wintypes.BOOL
    return IsWindow(hwnd)


def click_on_window(hwnd: ctypes.wintypes.HWND, x_wnd: int, y_wnd: int) -> bool:
    if not is_window(hwnd):
        return False

    x = int(x_wnd)
    y = int(y_wnd)
    point = client_to_screen(hwnd, create_point(x, y))
    x, y = convert_window_to_screen_coordinates(point.x, point.y)

    # move to position
    mi = MouseInput()
    mi.dx = x
    mi.dy = y
    mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
    if send_input_item(Input(mi)) == 0:
        return False

    # click
    mi.dx = 0
    mi.dy = 0
    mi.dwFlags = MOUSEEVENTF_LEFTDOWN
    if send_input_item(Input(mi)) == 0:
        return False

    # release
    mi.dx = 0
    mi.dy = 0
    mi.dwFlags = MOUSEEVENTF_LEFTUP
    if send_input_item(Input(mi)) == 0:
        return False

    # move in the upper left corner to not hinder detection
    point = client_to_screen(hwnd, create_point(0, 0))
    x, y = convert_window_to_screen_coordinates(point.x, point.y)
    mi.dx = x
    mi.dy = y
    mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
    if send_input_item(Input(mi)) == 0:
        return False

    return True


def get_module_name_from_window_handle(hWnd: ctypes.wintypes.HWND) -> str:
    """little wrapper around windows API calls to get the full filename of the exe of a window from its handle"""
    return get_module_file_name_ex_w(get_window_thread_process_id(hWnd))


def bring_window_to_top(hWnd: ctypes.wintypes.HWND) -> None:
    """forces the window for the given handle to always be on top of most windows"""
    set_foreground_window(hWnd)
    if is_iconic(hWnd):
        show_window(hWnd)
        # arbitrary value to wait until the restore animation has been played
        sleep(1000)
    set_window_pos(hWnd, HWND_TOPMOST, 0, 0, 0, 0,
                   SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW | SWP_FRAMECHANGED)


def set_foreground_window(hWnd: ctypes.wintypes.HWND) -> bool:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow"""
    SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
    SetForegroundWindow.argtypes = [ctypes.wintypes.HWND]
    SetForegroundWindow.restype = ctypes.wintypes.BOOL
    return SetForegroundWindow(hWnd)


def show_window(hWnd: ctypes.wintypes.HWND, nCmdShow: ctypes.wintypes.INT = SW_RESTORE) -> bool:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow"""
    ShowWindow = ctypes.windll.user32.ShowWindow
    ShowWindow.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.INT]
    ShowWindow.restype = ctypes.wintypes.BOOL
    return ShowWindow(hWnd, nCmdShow)


def is_iconic(hWnd: ctypes.wintypes.HWND) -> bool:
    """see https://docs.microsoft.com/de-de/windows/win32/api/winuser/nf-winuser-isiconic?redirectedfrom=MSDN"""
    IsIconic = ctypes.windll.user32.IsIconic
    IsIconic.argtypes = [ctypes.wintypes.HWND]
    IsIconic.restype = ctypes.wintypes.BOOL
    return IsIconic(hWnd)


def set_window_pos(hWnd: ctypes.wintypes.HWND, hWndInsertAfter: ctypes.wintypes.HWND = HWND_TOPMOST, X: int = 0,
                   Y: int = 0, cx: int = 0, cy: int = 0,
                   uFlags: ctypes.wintypes.UINT = SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW | SWP_FRAMECHANGED) -> bool:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos"""
    SetWindowPos = ctypes.windll.user32.SetWindowPos
    SetWindowPos.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.HWND, ctypes.wintypes.INT, ctypes.wintypes.INT,
                             ctypes.wintypes.INT, ctypes.wintypes.INT, ctypes.wintypes.UINT]
    SetWindowPos.restype = ctypes.wintypes.BOOL
    return SetWindowPos(hWnd, hWndInsertAfter, X, Y, cx, cy, uFlags)


def send_input(cInputs: ctypes.wintypes.UINT, pInputs: ctypes.wintypes.LPVOID,
               cbSize: ctypes.wintypes.INT) -> ctypes.wintypes.UINT:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput"""
    SendInput = ctypes.windll.user32.SendInput
    SendInput.argtypes = [ctypes.wintypes.UINT, ctypes.wintypes.LPVOID, ctypes.wintypes.INT]
    SendInput.restype = ctypes.wintypes.UINT
    return SendInput(cInputs, pInputs, cbSize)


def find_window(lpWindowName: str, lpClassName: str = None) -> ctypes.wintypes.HWND:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-findwindoww"""
    FindWindowW = ctypes.windll.user32.FindWindowW
    FindWindowW.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR]
    FindWindowW.restype = ctypes.wintypes.HWND
    return FindWindowW(lpClassName, lpWindowName)


def messagebox(message: str, hWnd: ctypes.wintypes.HWND = 0, title: str = '',
               flags: int = MB_OK | MB_ICONINFORMATION) -> int:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxw"""
    MessageBoxW = ctypes.windll.user32.MessageBoxW
    MessageBoxW.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.LPCWSTR,
                            ctypes.wintypes.LPCWSTR, ctypes.wintypes.UINT]
    MessageBoxW.restype = ctypes.wintypes.INT
    return MessageBoxW(hWnd, message, title, flags)


def get_window_thread_process_id(hWnd: ctypes.wintypes.HWND) -> ctypes.wintypes.DWORD:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid"""
    GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
    GetWindowThreadProcessId.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.LPDWORD]
    GetWindowThreadProcessId.restype = ctypes.wintypes.DWORD

    pid = ctypes.wintypes.DWORD()
    tid = GetWindowThreadProcessId(hWnd, ctypes.byref(pid))
    return pid.value


def get_module_file_name_ex_w(pid: ctypes.wintypes.DWORD) -> str:
    """see https://docs.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getmodulefilenameexw"""
    GetModuleFileName = ctypes.windll.psapi.GetModuleFileNameExW
    GetModuleFileName.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.HMODULE,
                                  ctypes.c_wchar_p, ctypes.wintypes.DWORD]
    GetModuleFileName.restype = ctypes.wintypes.DWORD

    filename = ctypes.create_unicode_buffer(MAX_PATH)
    hprocess = open_process(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    GetModuleFileName(hprocess, 0, filename, MAX_PATH)
    close_handle(hprocess)
    return filename.value


def get_process_image_file_name_w(pid: ctypes.wintypes.DWORD) -> str:
    """see https://docs.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessimagefilenamew"""
    GetProcessImageFileNameW = ctypes.windll.psapi.GetProcessImageFileNameW
    GetProcessImageFileNameW.argtypes = [ctypes.wintypes.HANDLE,
                                         ctypes.c_wchar_p, ctypes.wintypes.DWORD]
    GetProcessImageFileNameW.restype = ctypes.wintypes.DWORD

    filename = ctypes.create_unicode_buffer(MAX_PATH)
    hprocess = open_process(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    GetProcessImageFileNameW(hprocess, filename, MAX_PATH)
    close_handle(hprocess)
    return filename.value


def open_process(dwDesiredAccess: ctypes.wintypes.DWORD, bInheritHandle: ctypes.wintypes.BOOL,
                 dwProcessId: ctypes.wintypes.DWORD) -> ctypes.wintypes.HANDLE:
    """see https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess"""
    OpenProcess = ctypes.windll.Kernel32.OpenProcess
    OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
    OpenProcess.restype = ctypes.wintypes.HANDLE
    return OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)


def close_handle(hObject: ctypes.wintypes.HANDLE) -> bool:
    """see https://docs.microsoft.com/de-de/windows/win32/api/handleapi/nf-handleapi-closehandle"""
    CloseHandle = ctypes.windll.Kernel32.CloseHandle
    CloseHandle.argtypes = [ctypes.wintypes.HANDLE]
    CloseHandle.restype = ctypes.wintypes.BOOL
    return CloseHandle(hObject)


def get_last_error() -> int:
    return ctypes.windll.Kernel32.GetLastError()


def sleep(dwMilliseconds: ctypes.wintypes.DWORD) -> None:
    """see https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleep"""
    Sleep = ctypes.windll.Kernel32.Sleep
    Sleep.argtypes = [ctypes.wintypes.DWORD]
    Sleep.restype = None
    return Sleep(dwMilliseconds)


def open_clipboard(hWndNewOwner: ctypes.wintypes.HWND = None) -> bool:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-openclipboard"""
    OpenClipboard = ctypes.windll.user32.OpenClipboard
    OpenClipboard.argtypes = [ctypes.wintypes.HWND]
    OpenClipboard.restype = ctypes.wintypes.BOOL
    return OpenClipboard(hWndNewOwner)


def empty_clipboard() -> bool:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-emptyclipboard"""
    EmptyClipboard = ctypes.windll.user32.EmptyClipboard
    EmptyClipboard.argtypes = None
    EmptyClipboard.restype = ctypes.wintypes.BOOL
    return EmptyClipboard()


def set_clipboard_data(uFormat: ctypes.wintypes.UINT, hMem: ctypes.wintypes.HANDLE) -> ctypes.wintypes.HANDLE:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setclipboarddata"""
    SetClipboardData = ctypes.windll.user32.SetClipboardData
    SetClipboardData.argtypes = [ctypes.wintypes.UINT, ctypes.wintypes.HANDLE]
    SetClipboardData.restype = ctypes.wintypes.HANDLE
    return SetClipboardData(uFormat, hMem)


def close_clipboard() -> bool:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-closeclipboard"""
    CloseClipboard = ctypes.windll.user32.CloseClipboard
    CloseClipboard.argtypes = None
    CloseClipboard.restype = ctypes.wintypes.BOOL
    return CloseClipboard()


def global_lock(hMem: ctypes.wintypes.HGLOBAL) -> ctypes.wintypes.LPVOID:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-globallock"""
    GlobalLock = ctypes.windll.Kernel32.GlobalLock
    GlobalLock.argtypes = [ctypes.wintypes.HGLOBAL]
    GlobalLock.restype = ctypes.wintypes.LPVOID
    return GlobalLock(hMem)


def global_unlock(hMem: ctypes.wintypes.HGLOBAL) -> bool:
    """see https://docs.microsoft.com/de-de/windows/win32/api/winbase/nf-winbase-globalunlock"""
    GlobalUnlock = ctypes.windll.Kernel32.GlobalUnlock
    GlobalUnlock.argtypes = [ctypes.wintypes.HGLOBAL]
    GlobalUnlock.restype = ctypes.wintypes.BOOL
    return GlobalUnlock(hMem)


def global_size(hMem: ctypes.wintypes.HGLOBAL) -> ctypes.wintypes.SIZE:
    """see https://docs.microsoft.com/de-de/windows/win32/api/winbase/nf-winbase-globalsize"""
    GlobalSize = ctypes.windll.Kernel32.GlobalSize
    GlobalSize.argtypes = [ctypes.wintypes.HGLOBAL]
    GlobalSize.restype = ctypes.wintypes.SIZE
    return GlobalSize(hMem)


def get_system_metric(nIndex: int) -> int:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getsystemmetrics"""
    GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics
    GetSystemMetrics.argtypes = [ctypes.wintypes.INT]
    GetSystemMetrics.restype = ctypes.wintypes.INT
    return GetSystemMetrics(nIndex)


def get_client_rect(hWnd: ctypes.wintypes.HWND) -> ctypes.wintypes.RECT:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclientrect"""
    GetClientRect = ctypes.windll.user32.GetClientRect
    GetClientRect.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.LPRECT]
    GetClientRect.restype = ctypes.wintypes.BOOL
    rect = ctypes.wintypes.RECT()
    if GetClientRect(hWnd, ctypes.byref(rect)):
        return rect
    return None


def get_window_rect(hWnd: ctypes.wintypes.HWND) -> ctypes.wintypes.RECT:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclientrect"""
    GetWindowRect = ctypes.windll.user32.GetWindowRect
    GetWindowRect.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.LPRECT]
    GetWindowRect.restype = ctypes.wintypes.BOOL
    rect = ctypes.wintypes.RECT()
    if GetWindowRect(hWnd, ctypes.byref(rect)):
        return rect
    return None


def create_point(x: ctypes.wintypes.LONG = 0, y: ctypes.wintypes.LONG = 0) -> ctypes.wintypes.POINT:
    p = ctypes.wintypes.POINT()
    p.x = x
    p.y = y
    return p


def client_to_screen(hWnd: ctypes.wintypes.HWND, lpPoint: ctypes.wintypes.POINT) -> ctypes.wintypes.POINT:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclientrect"""
    ClientToScreen = ctypes.windll.user32.ClientToScreen
    ClientToScreen.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.LPPOINT]
    ClientToScreen.restype = ctypes.wintypes.BOOL
    if ClientToScreen(hWnd, ctypes.pointer(lpPoint)):
        return lpPoint
    return None


def map_window_points(hWndFrom: ctypes.wintypes.HWND, lpPoints: ctypes.wintypes.LPRECT,
                      hWndTo: ctypes.wintypes.HWND = None, cPoints: ctypes.wintypes.UINT = 2) -> ctypes.wintypes.INT:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mapwindowpoints"""
    MapWindowPoints = ctypes.windll.user32.MapWindowPoints
    MapWindowPoints.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.HWND, ctypes.wintypes.LPRECT,
                                ctypes.wintypes.UINT]
    MapWindowPoints.restype = ctypes.wintypes.INT
    return MapWindowPoints(hWndFrom, hWndTo, lpPoints, cPoints)


def window_rect_to_screen(hWnd: ctypes.wintypes.HWND, rect: ctypes.wintypes.RECT) -> (int, int):
    result = map_window_points(hWnd, ctypes.pointer(rect))
    if result == 0:
        raise ValueError('failed to translate window rect to screen. error code = {}'.format(get_last_error()))
    vertical = ctypes.wintypes.WORD(result)
    horizontal = ctypes.wintypes.WORD(result >> ctypes.sizeof(ctypes.wintypes.WORD))
    return horizontal.value, vertical.value


def get_device_context(hWnd: ctypes.wintypes.HWND = None) -> ctypes.wintypes.HDC:
    """see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getdc"""
    GetDC = ctypes.windll.user32.GetDC
    GetDC.argtypes = [ctypes.wintypes.HWND]
    GetDC.restype = ctypes.wintypes.HDC
    return GetDC(hWnd)


def release_device_context(hDC: ctypes.wintypes.HDC, hWnd: ctypes.wintypes.HWND = None) -> int:
    """see https://docs.microsoft.com/de-de/windows/win32/api/winuser/nf-winuser-releasedc"""
    ReleaseDC = ctypes.windll.user32.ReleaseDC
    ReleaseDC.argtypes = [ctypes.wintypes.HDC, ctypes.wintypes.HWND]
    ReleaseDC.restype = ctypes.wintypes.INT
    return ReleaseDC(hDC, hWnd)


def delete_object(ho: ctypes.wintypes.HGDIOBJ) -> bool:
    """see https://docs.microsoft.com/de-de/windows/win32/api/wingdi/nf-wingdi-deleteobject"""
    DeleteObject = ctypes.windll.Gdi32.DeleteObject
    DeleteObject.argtypes = [ctypes.wintypes.HGDIOBJ]
    DeleteObject.restype = ctypes.wintypes.BOOL
    return DeleteObject(ho)


def delete_dc(hdc: ctypes.wintypes.HDC) -> bool:
    """see https://docs.microsoft.com/de-de/windows/win32/api/wingdi/nf-wingdi-deletedc"""
    DeleteDC = ctypes.windll.Gdi32.DeleteDC
    DeleteDC.argtypes = [ctypes.wintypes.HDC]
    DeleteDC.restype = ctypes.wintypes.BOOL
    return DeleteDC(hdc)


def create_compatible_device_context(hdc: ctypes.wintypes.HDC) -> ctypes.wintypes.HDC:
    """see https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createcompatibledc"""
    CreateCompatibleDC = ctypes.windll.Gdi32.CreateCompatibleDC
    CreateCompatibleDC.argtypes = [ctypes.wintypes.HDC]
    CreateCompatibleDC.restype = ctypes.wintypes.HDC
    return CreateCompatibleDC(hdc)


def create_compatible_bitmap(hdc: ctypes.wintypes.HDC, cx: int, cy: int) -> ctypes.wintypes.HBITMAP:
    """see https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createcompatiblebitmap"""
    CreateCompatibleBitmap = ctypes.windll.Gdi32.CreateCompatibleBitmap
    CreateCompatibleBitmap.argtypes = [ctypes.wintypes.HDC, ctypes.wintypes.INT, ctypes.wintypes.INT]
    CreateCompatibleBitmap.restype = ctypes.wintypes.HBITMAP
    return CreateCompatibleBitmap(hdc, cx, cy)


def select_object(hdc: ctypes.wintypes.HDC, h: ctypes.wintypes.HGDIOBJ) -> ctypes.wintypes.HGDIOBJ:
    """see https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-selectobject"""
    SelectObject = ctypes.windll.Gdi32.SelectObject
    SelectObject.argtypes = [ctypes.wintypes.HDC, ctypes.wintypes.HGDIOBJ]
    SelectObject.restype = ctypes.wintypes.HGDIOBJ
    return SelectObject(hdc, h)


def bit_blt(hdc: ctypes.wintypes.HDC, x: int, y: int, cx: int, cy: int,
            hdcSrc: ctypes.wintypes.HDC, x1: int, y1: int, rop: ctypes.wintypes.DWORD) -> bool:
    """see https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-bitblt"""
    BitBlt = ctypes.windll.Gdi32.BitBlt
    BitBlt.argtypes = [ctypes.wintypes.HDC, ctypes.wintypes.INT, ctypes.wintypes.INT, ctypes.wintypes.INT,
                       ctypes.wintypes.INT, ctypes.wintypes.HDC, ctypes.wintypes.INT, ctypes.wintypes.INT,
                       ctypes.wintypes.DWORD]
    BitBlt.restype = ctypes.wintypes.BOOL
    return BitBlt(hdc, x, y, cx, cy, hdcSrc, x1, y1, rop)


def set_stretch_blt_mode(hdc: ctypes.wintypes.HDC, mode: int) -> int:
    """see https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-setstretchbltmode"""
    SetStretchBltMode = ctypes.windll.Gdi32.SetStretchBltMode
    SetStretchBltMode.argtypes = [ctypes.wintypes.HDC, ctypes.wintypes.INT]
    SetStretchBltMode.restype = ctypes.wintypes.HDC
    return SetStretchBltMode(hdc, mode)


def get_di_bits(hdc: ctypes.wintypes.HDC, hbm: ctypes.wintypes.HBITMAP, start: ctypes.wintypes.UINT,
                cLines: ctypes.wintypes.UINT, lpvBits: ctypes.wintypes.LPVOID,
                lpbmi: ctypes.wintypes.LPVOID, usage: ctypes.wintypes.UINT) -> int:
    """see https://docs.microsoft.com/de-de/windows/win32/api/wingdi/nf-wingdi-getdibits?redirectedfrom=MSDN"""
    GetDIBits = ctypes.windll.Gdi32.GetDIBits
    GetDIBits.argtypes = [ctypes.wintypes.HDC, ctypes.wintypes.HBITMAP, ctypes.wintypes.UINT, ctypes.wintypes.UINT,
                          ctypes.wintypes.LPVOID, ctypes.wintypes.LPVOID, ctypes.wintypes.UINT]
    GetDIBits.restype = ctypes.wintypes.INT
    return GetDIBits(hdc, hbm, start, cLines, lpvBits, lpbmi, usage)


def get_bitmapinfo_from_bitmap(hdc: ctypes.wintypes.HDC, hbm: ctypes.wintypes.HBITMAP) -> [BITMAPINFO, bytearray]:
    """wrapper function to extract pixel data from a bitmap handle"""
    info = BITMAPINFO()
    info.bmiHeader.biSize = ctypes.sizeof(info.bmiHeader)
    if 0 == get_di_bits(hdc, hbm, 0, 0, None, ctypes.byref(info), DIB_RGB_COLORS):
        return None, None
    pixels = bytearray(info.bmiHeader.biSizeImage)
    char_array = ctypes.c_char * len(pixels)
    if 0 == get_di_bits(hdc, hbm, 0, info.bmiHeader.biHeight, char_array.from_buffer(pixels), ctypes.byref(info),
                        DIB_RGB_COLORS):
        return None, None
    return info, pixels


def get_screenshot(hwnd=None) -> (bytearray, int, int):
    if hwnd is None:
        return None, 0, 0
    bring_window_to_top(hwnd)

    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    old = saveDC.SelectObject(saveBitMap)
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    saveDC.SelectObject(old)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        return bmpstr, bmpinfo['bmWidth'], bmpinfo['bmHeight']
    return None, 0, 0

#
#
# def ole_create_picture_indirect(lpPictDesc: ctypes.wintypes.LPPICTDESC, riid: ctypes.wintypes.REFIID,
#                                 fOwn: ctypes.wintypes.BOOL, lplpvObj: ctypes.wintypes.LPVOID) -> int:
#     """see https://docs.microsoft.com/en-us/windows/win32/api/olectl/nf-olectl-olecreatepictureindirect"""
#     OleCreatePictureIndirect = ctypes.windll.OleAut32.OleCreatePictureIndirect
#     OleCreatePictureIndirect.argtypes = [ctypes.wintypes.LPPICTDESC, ctypes.wintypes.REFIID,
#                                          ctypes.wintypes.BOOL, ctypes.wintypes.LPVOID]
#     OleCreatePictureIndirect.restype = ctypes.wintypes.INT
#     return OleCreatePictureIndirect(lpPictDesc, riid, fOwn, lplpvObj)
#
#
# def create_stream_on_h_global(hGlobal: ctypes.wintypes.HGLOBAL, fDeleteOnRelease: ctypes.wintypes.BOOL,
#                               ppstm: ctypes.wintypes.LPVOID) -> int:
#     """see https://docs.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-createstreamonhglobal"""
#     CreateStreamOnHGlobal = ctypes.windll.Ole32.CreateStreamOnHGlobal
#     CreateStreamOnHGlobal.argtypes = [ctypes.wintypes.HGLOBAL, ctypes.wintypes.BOOL, ctypes.wintypes.LPVOID]
#     CreateStreamOnHGlobal.restype = ctypes.wintypes.INT
#     return CreateStreamOnHGlobal(hGlobal, fDeleteOnRelease, ppstm)
