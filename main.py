import logging
import win32
import cv2
import numpy as np

# title of the game window to search for
TITLE_BEJEWELED1 = 'Bejeweled Deluxe 1.87'
# TITLE_BEJEWELED2 = 'Bejeweled 2 Deluxe 1.0'


def get_screenshot():
    """grabs a screenshot and converts it to a numpy array usable by opencv"""
    hWnd = win32.find_window(TITLE_BEJEWELED1)
    if hWnd is None:
        logging.error("unable to find window")
        return None
    win32.bring_window_to_top(hWnd)

    rect = win32.get_client_rect(hWnd)
    if rect is None:
        logging.error("unable to get window dimensions")
        return None
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    window_rect = win32.get_window_rect(hWnd)
    if window_rect is None:
        logging.error("unable to get window dimensions")
        return None

    try:
        hScreen = win32.get_device_context()
        hDC = win32.create_compatible_device_context(hScreen)
        hBitmap = win32.create_compatible_bitmap(hScreen, width, height)

        old_obj = win32.select_object(hDC, hBitmap)
        info = None
        pixels = None
        try:
            # magic number 4 to account for window boarders
            if win32.bit_blt(hDC, 0, 0, width, height, hScreen, window_rect.right - width - 4,
                                 window_rect.bottom - height - 4, win32.SRCCOPY):
                info, pixels = win32.get_bitmapinfo_from_bitmap(hDC, hBitmap)
        finally:
            win32.select_object(hDC, old_obj)

        if pixels is None:
            logging.error("unable to retrieve pixel data from screen capture")
            return None

        arr = np.frombuffer(pixels, dtype=np.uint8)
        arr.shape = (info.bmiHeader.biHeight, info.bmiHeader.biWidth, 4)
        return np.flipud(arr)

    finally:
        win32.delete_object(hBitmap)
        win32.delete_dc(hDC)
        win32.release_device_context(None, hScreen)


img = get_screenshot()
if img is not None:
    cv2.imshow('test', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
exit(0)
