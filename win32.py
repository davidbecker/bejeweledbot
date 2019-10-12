import ctypes
import ctypes.wintypes

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

MAX_PATH = 256

PROCESS_TERMINATE = 0x0001
PROCESS_CREATE_THREAD = 0x0002
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_DUP_HANDLE = 0x0040
PROCESS_CREATE_PROCESS = 0x0080
PROCESS_QUERY_INFORMATION = 0x0400


def get_module_name_from_window_handle(hWnd: ctypes.wintypes.HWND):
    """little wrapper around windows API calls to get the full filename of the exe of a window"""
    return get_module_file_name_ex_w(get_window_thread_process_id(hWnd))


def bring_window_to_top(hWnd: ctypes.wintypes.HWND):
    """forces the window for the given handle to always be on top of most windows"""
    ctypes.windll.user32.SetForegroundWindow(hWnd)
    ctypes.windll.user32.SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0,
                                      SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW | SWP_FRAMECHANGED)


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
