import ctypes
import ctypes.wintypes

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


def select_object(hdc: ctypes.wintypes.HDC, h:  ctypes.wintypes.HGDIOBJ) -> ctypes.wintypes.HGDIOBJ:
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
