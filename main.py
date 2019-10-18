import logging
import win32
import cv2
import io
import numpy

# title of the game window to search for
TITLE_BEJEWELED1 = 'Bejeweled Deluxe 1.87'
# TITLE_BEJEWELED2 = 'Bejeweled 2 Deluxe 1.0'

DATA_PATH = 'R:\\Bejeweled\\'




def copy_to_clipboard():
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

    try:
        hScreen = win32.get_device_context()
        hDC = win32.create_compatible_device_context(hScreen)
        hBitmap = win32.create_compatible_bitmap(hScreen, width, height)

        old_obj = win32.select_object(hDC, hBitmap)
        try:
            bRet = win32.bit_blt(hDC, 0, 0, width, height, hScreen, window_rect.left, window_rect.top, win32.SRCCOPY)
            info, pixels = win32.get_bitmapinfo_from_bitmap(hDC, hBitmap)
        finally:
            win32.select_object(hDC, old_obj)

        if pixels is None:
            logging.error("unable to retrieve pixel data from screen capture")
            return None

        import ctypes
        # TODO convert to cv2 image directly
        fileheader = win32.BITMAPFILEHEADER()
        fileheader.magic = 0x4d42  # "BM" magic word
        fileheader.bOffBits = ctypes.sizeof(fileheader) + info.bmiHeader.biSize
        fileheader.bfSize = fileheader.bOffBits + info.bmiHeader.biSizeImage
        fileheader.bfReserved1 = 0
        fileheader.bfReserved2 = 0
        # fileheader.bOffBits = ctypes.sizeof(info)

        with open(DATA_PATH + 'somefile.bmp', 'wb') as the_file:
            the_file.write(b'BM')

            fakefile = io.BytesIO(fileheader)

            #io.BytesIO
            #the_file.write(fileheader)
            # the_file.write(info)
            # the_file.write(pixels)

        buffer = io.BytesIO()
        buffer.write(fileheader)

        with open(DATA_PATH + 'somefile.bmp', "wb") as f:
            f.write(buffer.getvalue())

        # handle = win32.global_lock(hBitmap)
        # if handle != 0:
        #     size = win32.global_size(handle)
        #     if (size != 0):
        #         import ctypes;
        #         # data = ctypes.from_address(handle)
        #         data = list((size * ctypes.c_byte).from_address(handle))
        #     win32.global_lock(handle)

        #win32.open_clipboard()
        #win32.empty_clipboard()
        #win32.set_clipboard_data(win32.CF_BITMAP, hBitmap)
        #win32.close_clipboard()
    finally:
        win32.delete_object(hBitmap)
        win32.delete_dc(hDC)
        win32.release_device_context(None, hScreen)


def imshow():
    # img = cv2.getWindowImageRect(TITLE_BEJEWELED1)
    img = cv2.imread(DATA_PATH + 'test.png', cv2.IMREAD_GRAYSCALE)
    cv2.imshow('test', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


copy_to_clipboard()
#imshow()
exit(0)
