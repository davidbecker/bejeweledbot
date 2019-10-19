import logging
import win32
import cv2
import numpy as np

# title of the game window to search for
TITLE_BEJEWELED1 = 'Bejeweled Deluxe 1.87'
# TITLE_BEJEWELED2 = 'Bejeweled 2 Deluxe 1.0'

GEMSHEET = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Bejeweled Deluxe\\images\\gemsheet6.png'
# number of gem types
NUM_GEMS = 7
GEM_WIDTH = GEM_HEIGHT = 52

# colors in BGR to draw debug output
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_ORANGE = (0, 128, 255)
COLOR_PURPLE = (128, 0, 128)
COLOR_WHITE = (255, 255, 255)

def find_game_window_handle():
    return win32.find_window(TITLE_BEJEWELED1)


def get_screenshot() -> np.ndarray:
    """grabs a screenshot and converts it to a numpy array usable by opencv"""
    hWnd = find_game_window_handle()
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
        # image needs to be flipped
        arr = np.flipud(arr)
        return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)

    finally:
        win32.delete_object(hBitmap)
        win32.delete_dc(hDC)
        win32.release_device_context(None, hScreen)


def get_game_folder() -> str:
    """tries to find the full path where the exe was started from"""
    handle = find_game_window_handle()
    if handle is None:
        return None
    exe = win32.get_module_name_from_window_handle(handle)
    if exe is None or exe.__len__() == 0:
        return None
    path, file = os.path.split(exe)
    return path


def gray_conversione(image):
    """converts an image to grayscale - stolen from https://stackoverflow.com/a/51287214"""
    gray = 0.07 * image[:, :, 2] + 0.72 * image[:, :, 1] + 0.21 * image[:, :, 0]
    return gray.astype(np.uint8)


def debug_show_image(image) -> bool:
    if image is None:
        return False
    cv2.imshow('debug', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return True


def match_template(img_grayscale, template, threshold=0.9):
    res = cv2.matchTemplate(img_grayscale, template, cv2.TM_CCOEFF_NORMED)
    matches = np.where(res >= threshold)
    return matches


def draw_matches(loc, image, color=COLOR_RED):
    for p in zip(*loc[::-1]):
        cv2.rectangle(image, p, (p[0] + GEM_WIDTH, p[1] + GEM_HEIGHT), color, 2)


img = get_screenshot()
imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# load the tile sheet with all the gems
# img_gemssheet = cv2.imread(GEMSHEET, cv2.IMREAD_GRAYSCALE)
img_gemssheet = cv2.cvtColor(cv2.imread(GEMSHEET), cv2.COLOR_BGR2GRAY)

# extract all possible states for each color
img_gems_yellow = img_gemssheet[0:2*GEM_HEIGHT]
img_gems_white = img_gemssheet[2*GEM_HEIGHT:4*GEM_HEIGHT]
img_gems_blue = img_gemssheet[4*GEM_HEIGHT:6*GEM_HEIGHT]
img_gems_red = img_gemssheet[6*GEM_HEIGHT:8*GEM_HEIGHT]
img_gems_purple = img_gemssheet[8*GEM_HEIGHT:10*GEM_HEIGHT]
img_gems_orange = img_gemssheet[10*GEM_HEIGHT:12*GEM_HEIGHT]
img_gems_green = img_gemssheet[12*GEM_HEIGHT:14*GEM_HEIGHT]

# extract one gem state per color to use for template matching
img_gem_yellow = img_gems_yellow[0:GEM_HEIGHT, 0:GEM_WIDTH]
img_gem_white = img_gems_white[0:GEM_HEIGHT, 0:GEM_WIDTH]
img_gem_blue = img_gems_blue[0:GEM_HEIGHT, 0:GEM_WIDTH]
img_gem_red = img_gems_red[0:GEM_HEIGHT, 0:GEM_WIDTH]
img_gem_purple = img_gems_purple[0:GEM_HEIGHT, 0:GEM_WIDTH]
img_gem_orange = img_gems_orange[0:GEM_HEIGHT, 0:GEM_WIDTH]
img_gem_green = img_gems_green[0:GEM_HEIGHT, 0:GEM_WIDTH]

# _, threshold_yellow = cv2.threshold(img_gem_yellow, 128, 255, cv2.THRESH_BINARY)
# _, threshold_white = cv2.threshold(img_gem_white, 128, 255, cv2.THRESH_BINARY)
# _, threshold_blue = cv2.threshold(img_gem_blue, 128, 255, cv2.THRESH_BINARY)
# _, threshold_red = cv2.threshold(img_gem_red, 128, 255, cv2.THRESH_BINARY)
# _, threshold_purple = cv2.threshold(img_gem_purple, 128, 255, cv2.THRESH_BINARY)
# _, threshold_orange = cv2.threshold(img_gem_orange, 128, 255, cv2.THRESH_BINARY)
# _, threshold_green = cv2.threshold(img_gem_green, 128, 255, cv2.THRESH_BINARY)


matches_red = match_template(imggray, img_gem_red, threshold=.83)
matches_green = match_template(imggray, img_gem_green)
matches_blue = match_template(imggray, img_gem_blue)
matches_yellow = match_template(imggray, img_gem_yellow)
matches_orange = match_template(imggray, img_gem_orange)
matches_purple = match_template(imggray, img_gem_purple, threshold=.7)
matches_white = match_template(imggray, img_gem_white)

draw_matches(matches_red, img)
draw_matches(matches_green, img, color=COLOR_GREEN)
draw_matches(matches_blue, img, color=COLOR_BLUE)
draw_matches(matches_yellow, img, color=COLOR_YELLOW)
draw_matches(matches_orange, img, color=COLOR_ORANGE)
draw_matches(matches_purple, img, color=COLOR_PURPLE)
draw_matches(matches_white, img, color=COLOR_WHITE)
debug_show_image(img)


exit(0)
