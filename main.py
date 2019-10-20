import logging
import win32
import cv2
import numpy as np
import model


# title of the game window to search for
TITLE_BEJEWELED1 = 'Bejeweled Deluxe 1.87'
# TITLE_BEJEWELED2 = 'Bejeweled 2 Deluxe 1.0'

# filename to use when dumping files
DUMP_FILENAME = 'dump'

# hardcoded for now
GEMSHEET = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Bejeweled Deluxe\\images\\gemsheet6.png'
# gem dimensions in pixels
GEM_WIDTH = GEM_HEIGHT = 52

# colors in BGR to draw debug output
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_ORANGE = (0, 128, 255)
COLOR_PURPLE = (128, 0, 128)
COLOR_WHITE = (255, 255, 255)

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
        # strip alpha channel
        return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)

    finally:
        win32.delete_object(hBitmap)
        win32.delete_dc(hDC)
        win32.release_device_context(None, hScreen)


# def get_game_folder() -> str:
#     """tries to find the full path where the exe was started from"""
#     handle = find_game_window_handle()
#     if handle is None:
#         return None
#     exe = win32.get_module_name_from_window_handle(handle)
#     if exe is None or exe.__len__() == 0:
#         return None
#     path, file = os.path.split(exe)
#     return path


# def gray_conversione(image):
#     """converts an image to grayscale - stolen from https://stackoverflow.com/a/51287214"""
#     gray = 0.07 * image[:, :, 2] + 0.72 * image[:, :, 1] + 0.21 * image[:, :, 0]
#     return gray.astype(np.uint8)


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


def get_min_max_point(matches, min_point: tuple = None, max_point: tuple = None):
    """extracts the minimum and maximum point out given tuples"""
    x_min = y_min = x_max = y_max = None

    if min_point is not None:
        x_min = min_point[0]
        y_min = min_point[1]

    if max_point is not None:
        x_max = min_point[0]
        y_max = min_point[1]

    for p in zip(*matches[::-1]):
        if x_min is None:
            x_min = p[0]
        elif x_min > p[0]:
            x_min = p[0]

        if y_min is None:
            y_min = p[1]
        elif y_min > p[1]:
            y_min = p[1]

        if x_max is None:
            x_max = p[0]
        elif x_max < p[0]:
            x_max = p[0]

        if y_max is None:
            y_max = p[1]
        elif y_max < p[1]:
            y_max = p[1]

    return (x_min, y_min), (x_max, y_max)


def translate_picture_coordinates_to_model(min_point: tuple, max_point: tuple, point: tuple) -> (int, int):
    """tries to map a found match to the game board"""
    x = y = -1
    # the matches represent the upper left corner of the found image
    if point is None or point.__len__() != 2:
        raise ValueError('approximate_matches - invalid point {} given'.format(point))

    # there are two different frames of references:
    # in the image (0,0) references the upper left corner, while in the game model these coordinates represent the
    # lower left corner. so (0, 0) on the game board is at (min_point[0], max_point[1])
    for i in range(model.COUNT_GEMS_H):
        x_tmp = min_point[0] + x * GEM_WIDTH
        # add fussiness to account for not perfectly aligned pixels
        if x_tmp + GEM_WIDTH / 4 > point[0] > x_tmp - GEM_WIDTH / 4:
            break
        if x_tmp < point[0]:
            x = x + 1
        if x_tmp > max_point[0]:
            break
    for i in range(model.COUNT_GEMS_V):
        y_tmp = max_point[1] - y * GEM_HEIGHT
        # add fussiness to account for not perfectly aligned pixels
        if y_tmp + GEM_HEIGHT / 4 > point[1] > y_tmp - GEM_HEIGHT / 4:
            break
        if y_tmp > point[1]:
            y = y + 1
        if y_tmp < min_point[1]:
            break
    return x, y


def get_game_state(screenshot) -> model.GameState:
    if screenshot is None:
        return None
    imggray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # find all matches for each gem type
    matches_red = match_template(imggray, img_gem_red, threshold=.83)
    matches_green = match_template(imggray, img_gem_green)
    matches_blue = match_template(imggray, img_gem_blue)
    matches_yellow = match_template(imggray, img_gem_yellow)
    matches_orange = match_template(imggray, img_gem_orange)
    matches_purple = match_template(imggray, img_gem_purple, threshold=.7)
    matches_white = match_template(imggray, img_gem_white)

    # get the outer bounds of the gaming area
    min_point = max_point = None
    min_point, max_point = get_min_max_point(matches_red, min_point, max_point)
    min_point, max_point = get_min_max_point(matches_green, min_point, max_point)
    min_point, max_point = get_min_max_point(matches_blue, min_point, max_point)
    min_point, max_point = get_min_max_point(matches_yellow, min_point, max_point)
    min_point, max_point = get_min_max_point(matches_orange, min_point, max_point)
    min_point, max_point = get_min_max_point(matches_purple, min_point, max_point)
    min_point, max_point = get_min_max_point(matches_white, min_point, max_point)

    gs = model.GameState()
    # add a gem for each found match to our game state
    for p in zip(*matches_yellow[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        gs.add_gem(x, y, model.GemType.YELLOW)
    for p in zip(*matches_white[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        gs.add_gem(x, y, model.GemType.WHITE)
    for p in zip(*matches_blue[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        gs.add_gem(x, y, model.GemType.BLUE)
    for p in zip(*matches_red[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        gs.add_gem(x, y, model.GemType.RED)
    for p in zip(*matches_purple[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        gs.add_gem(x, y, model.GemType.PURPLE)
    for p in zip(*matches_orange[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        gs.add_gem(x, y, model.GemType.ORANGE)
    for p in zip(*matches_green[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        gs.add_gem(x, y, model.GemType.GREEN)

    complete = gs.check_board_complete()
    if complete:
        gs.phase = model.GamePhase.IN_GAME

    if gs.phase == model.GamePhase.UNKNOWN:
        import time
        filename = DUMP_FILENAME + str(int(time.time()))
        log_file_name = filename + '.log'
        logging.error('failed to get game state - dumping to {}'.format(log_file_name))

        fh = logging.FileHandler(filename)
        fh.setLevel(logging.DEBUG)
        file_logger = logging.getLogger("file")
        file_logger.addHandler(fh)
        file_logger.error('failed to get complete game state')
        file_logger.info(gs)
        cv2.imwrite(filename + '.bmp', screenshot)
        exit(-1)
    return gs


# img = get_screenshot()
img = cv2.imread("screenshot.bmp")
game_state = get_game_state(img)

exit(0)
