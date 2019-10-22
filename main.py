import logging
import controller_naive
import win32
import cv2
import os
import numpy as np
import model
import time

# title of the game window to search for
TITLE_BEJEWELED1 = 'Bejeweled Deluxe 1.87'
# TITLE_BEJEWELED2 = 'Bejeweled 2 Deluxe 1.0'

# filename to use when dumping files
DUMP_FILENAME = 'dump'
DUMP_LOCATION = 'R:\\dump\\'

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
img_gems_yellow = img_gemssheet[0:2 * GEM_HEIGHT]
img_gems_white = img_gemssheet[2 * GEM_HEIGHT:4 * GEM_HEIGHT]
img_gems_blue = img_gemssheet[4 * GEM_HEIGHT:6 * GEM_HEIGHT]
img_gems_red = img_gemssheet[6 * GEM_HEIGHT:8 * GEM_HEIGHT]
img_gems_purple = img_gemssheet[8 * GEM_HEIGHT:10 * GEM_HEIGHT]
img_gems_orange = img_gemssheet[10 * GEM_HEIGHT:12 * GEM_HEIGHT]
img_gems_green = img_gemssheet[12 * GEM_HEIGHT:14 * GEM_HEIGHT]

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


def get_screenshot():
    raw, width, height = win32.get_screenshot(find_game_window_handle())
    if raw is None:
        return None
    arr = np.frombuffer(raw, dtype=np.uint8)
    arr.shape = (height, width, 4)
    # strip alpha channel
    return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)


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
        x_max = max_point[0]
        y_max = max_point[1]

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


def translate_model_positions_to_picture_coordinates(min_point: tuple, max_point: tuple,
                                                     model_points: list) -> list:
    """translates a list of model coordinates into picture coordinates"""
    # no offset to account for pixel mismatch for now, clicking on the middle of the gem should suffice
    x0 = min_point[0]
    y0 = max_point[1]
    ret = []
    for p in model_points:
        ret.append((x0 + p[0] * GEM_WIDTH, y0 - p[1] * GEM_HEIGHT))
    return ret


def dump(msg: str = 'dump content to file', state: model.GameState = None, image=None) -> None:
    """dumps current game state to a file as well as saving the screenshot"""
    filename = DUMP_FILENAME + str(int(time.time()))

    if not os.path.exists(DUMP_LOCATION):
        os.makedirs(DUMP_LOCATION)

    # if we have a dumping location we dump there instead of the current location
    if os.path.exists(DUMP_LOCATION):
        filename = DUMP_LOCATION + filename

    log_file_name = filename + '.log'
    logging.error('{} - dumping to {}'.format(msg, log_file_name))

    fh = logging.FileHandler(log_file_name)
    fh.setLevel(logging.DEBUG)
    file_logger = logging.getLogger("file")
    file_logger.addHandler(fh)
    file_logger.error(msg)
    if state is not None:
        file_logger.info(state)
    if image is not None:
        cv2.imwrite(filename + '.bmp', image)


def fill_game_state(screenshot, gs: model.GameState, dump_on_error: bool = False, terminate_on_error: bool = False) -> (tuple, tuple):
    if screenshot is None:
        raise ValueError('no screenshot given')
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

    if min_point is None or max_point is None:
        raise Exception('failed to find game area')

    gs.reset()

    # add a gem for each found match to our game state
    for p in zip(*matches_yellow[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        if not gs.add_gem(x, y, model.GemType.YELLOW):
            if dump_on_error:
                dump('invalid position for yellow gem', state=gs, image=screenshot)
            if terminate_on_error:
                exit(-1)
    for p in zip(*matches_white[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        if not gs.add_gem(x, y, model.GemType.WHITE):
            if dump_on_error:
                dump('invalid position for white gem', state=gs, image=screenshot)
            if terminate_on_error:
                exit(-1)
    for p in zip(*matches_blue[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        if not gs.add_gem(x, y, model.GemType.BLUE):
            if dump_on_error:
                dump('invalid position for blue gem', state=gs, image=screenshot)
            if terminate_on_error:
                exit(-1)
    for p in zip(*matches_red[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        if not gs.add_gem(x, y, model.GemType.RED):
            if dump_on_error:
                dump('invalid position for red gem', state=gs, image=screenshot)
            if terminate_on_error:
                exit(-1)
    for p in zip(*matches_purple[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        if not gs.add_gem(x, y, model.GemType.PURPLE):
            if dump_on_error:
                dump('invalid position for purple gem', state=gs, image=screenshot)
            if terminate_on_error:
                exit(-1)
    for p in zip(*matches_orange[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        if not gs.add_gem(x, y, model.GemType.ORANGE):
            if dump_on_error:
                dump('invalid position for orange gem', state=gs, image=screenshot)
            if terminate_on_error:
                exit(-1)
    for p in zip(*matches_green[::-1]):
        x, y = translate_picture_coordinates_to_model(min_point, max_point, p)
        if not gs.add_gem(x, y, model.GemType.GREEN):
            if dump_on_error:
                dump('invalid position for green gem', state=gs, image=screenshot)
            if terminate_on_error:
                exit(-1)

    complete = gs.check_board_complete()
    if complete:
        gs.phase = model.GamePhase.IN_GAME

    # if gs.phase == model.GamePhase.UNKNOWN:
    #     dump(msg='failed to get game state', state=gs, image=screenshot)
    #     exit(-1)

    # min_point and max_point are the coordinates of the upper left corner of each tile, so we change
    # them to point to the center
    try:
        return (min_point[0] + GEM_WIDTH / 2, min_point[1] + GEM_HEIGHT / 2), (
            max_point[0] + GEM_WIDTH / 2, max_point[1] + GEM_HEIGHT / 2)
    except TypeError:
        return None, None


num_tries = 0
max_tries = 30

while num_tries < max_tries:
    img = get_screenshot()
    # img = cv2.imread("screenshot.bmp")

    if img is None:
        exit(-1)
    game_state = model.GameState()
    game_area_min, game_area_max = fill_game_state(img, game_state)

    hwnd = find_game_window_handle()

    controller = controller_naive.NaiveGameController()
    if controller_naive.NaiveGameController.can_handle_game_state(controller, game_state):
        print(game_state)
        point1, point2 = controller_naive.NaiveGameController.next_turn(controller_naive, game_state)
        if point1 is None or point2 is None:
            dump('no possible turn', state=game_state, image=img)
            exit(-1)
        print(game_state)
        logging.info('next turn: {} to {}'.format(point1, point2))
        win32.bring_window_to_top(hwnd)
        for c in translate_model_positions_to_picture_coordinates(game_area_min, game_area_max, (point1, point2)):
            win32.click_on_window(hwnd, c[0], c[1])
        num_tries = 0
    else:
        logging.debug(game_state)
        # allow for more time to not annoy me too much
        waiting = 1.5
        if num_tries > 5:
            waiting = waiting + .5
        logging.info('can\'t handle game state. wait {} seconds and repeat'.format(waiting))
        time.sleep(waiting)
        # click in upper left corner to clear selection
        win32.click_on_window(hwnd, 0, 0)
    num_tries = num_tries + 1

exit(0)
