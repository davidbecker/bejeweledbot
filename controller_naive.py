import controller_base
from model import *
import logging


class NaiveGameController(controller_base.AbstractGameController):
    """naive controller class that computes the next game turn based on pre programmed rules"""

    def next_turn(self, game_state: GameState) -> ((int, int), (int, int)):
        point1 = point2 = (0, 0)
        last_gem = GemType.UNKNOWN
        count = 0

        # TODO implement scan for vertical match
        for x in range(COUNT_GEMS_H):
            for y in reversed(range(COUNT_GEMS_V)):
                if game_state.gems[x][y] != last_gem:
                    # gem type has changed
                    if count == 1:
                        # check if we have a V shape
                        if y - 1 >= 0 and game_state.gems[x][y - 1] == last_gem:
                            if x - 1 >= 0 and game_state.gems[x - 1][y] == last_gem:
                                point1 = (x, y)
                                point2 = (x - 1, y)
                            if x + 1 < COUNT_GEMS_H and game_state.gems[x + 1][y] == last_gem:
                                point1 = (x, y)
                                point2 = (x + 1, y)
                    elif count > 1:
                        # A
                        # B
                        # A
                        # A
                        if y + (count + 2) < COUNT_GEMS_V and game_state.gems[x][y + (count + 2)] == last_gem:
                            point1 = (x, y + (count + 2))
                            point2 = (x, y + (count + 1))
                        # A
                        # A
                        # B
                        # A
                        elif y - 1 >= 0 and game_state.gems[x][y - 1] == last_gem:
                            point1 = (x, y)
                            point2 = (x, y - 1)
                        # A C
                        # A D
                        # B A
                        elif x + 1 < COUNT_GEMS_H and game_state.gems[x + 1][y] == last_gem:
                            point1 = (x, y)
                            point2 = (x + 1, y)
                        # C A
                        # D A
                        # A B
                        elif x - 1 >= 0 and game_state.gems[x - 1][y] == last_gem:
                            point1 = (x, y)
                            point2 = (x - 1, y)
                        # B A
                        # A C
                        # A D
                        elif x + 1 < COUNT_GEMS_H and y + 3 < COUNT_GEMS_V and game_state.gems[x + 1][y + 3] == last_gem:
                            point1 = (x, y + 3)
                            point2 = (x + 1, y + 3)
                        # A B
                        # C A
                        # D A
                        elif x - 1 >= 0 and y + 3 < COUNT_GEMS_V and game_state.gems[x - 1][y + 3] == last_gem:
                            point1 = (x, y + 3)
                            point2 = (x - 1, y + 3)

                    count = 0
                elif y == 0 and count == 1:
                    # check for
                    # A
                    # B
                    # A
                    # A
                    # at the end of the board
                    if game_state.gems[x][y + (count + 2)] == last_gem:
                        point1 = (x, y + (count + 2))
                        point2 = (x, y + (count + 1))

                count = count + 1
                last_gem = game_state.gems[x][y]

                if controller_base.check_valid_turn(point1, point2):
                    return point1, point2
                elif point1 != (0, 0) and point2 != (0, 0):
                    logging.debug('invalid turn selected: x={},y={} {} -> {}'.format(x, y, point1, point2))

                point1 = point2 = (0, 0)

            # reset gem on next row
            last_gem = GemType.UNKNOWN
            count = 0

        # scan if we can get a horizontal match
        for y in reversed(range(COUNT_GEMS_V)):
            for x in range(COUNT_GEMS_H):
                if game_state.gems[x][y] != last_gem:
                    # gem type has changed
                    if count == 1:
                        # check if we have a V shape
                        if x + 1 < COUNT_GEMS_H and game_state.gems[x + 1][y] == last_gem:
                            if y + 1 < COUNT_GEMS_V and game_state.gems[x][y + 1] == last_gem:
                                point1 = (x, y)
                                point2 = (x, y + 1)
                            elif y - 1 >= 0 and game_state.gems[x][y - 1] == last_gem:
                                point1 = (x, y)
                                point2 = (x, y - 1)
                    elif count > 1:
                        # was A B A A
                        if x - (count + 2) >= 0 and game_state.gems[x - (count + 2)][y] == last_gem:
                            point1 = (x - (count + 2), y)
                            point2 = (x - (count + 1), y)
                        # was A A B A
                        elif x + 1 < COUNT_GEMS_H and game_state.gems[x + 1][y] == last_gem:
                            point1 = (x, y)
                            point2 = (x + 1, y)
                        # A C D
                        # B A A
                        elif x - (count + 1) >= 0 and y + 1 < COUNT_GEMS_V and \
                                game_state.gems[x - (count + 1)][y + 1] == last_gem:
                            point1 = (x - (count + 1), y)
                            point2 = (x - (count + 1), y + 1)
                        # C D A
                        # A A B
                        elif y + 1 < COUNT_GEMS_V and game_state.gems[x][y + 1] == last_gem:
                            point1 = (x, y)
                            point2 = (x, y + 1)
                        # B A A
                        # A C D
                        elif x - (count + 1) >= 0 and y - 1 >= 0 and \
                                game_state.gems[x - (count + 1)][y - 1] == last_gem:
                            point1 = (x - (count + 1), y)
                            point2 = (x - (count + 1), y - 1)
                        # A A B
                        # C D A
                        elif y - 1 >= 0 and game_state.gems[x][y - 1] == last_gem:
                            point1 = (x, y)
                            point2 = (x, y - 1)

                    count = 0
                elif x == COUNT_GEMS_H - 1 and count == 1:
                    # check for A B A A at the end of the board
                    if game_state.gems[x - (count + 2)][y] == last_gem:
                        point1 = (x - (count + 2), y)
                        point2 = (x - (count + 1), y)
                    # check for
                    # B A A
                    # A C D
                    # at the end of the board
                    elif y - 1 > 0 and game_state.gems[x - (count + 1)][y - 1] == last_gem:
                        point1 = (x - (count + 1), y)
                        point2 = (x - (count + 1), y - 1)
                    # check for
                    # A C D
                    # B A A
                    # at the end of the board
                    elif y + 1 < COUNT_GEMS_V and game_state.gems[x - (count + 1)][y + 1] == last_gem:
                        point1 = (x - (count + 1), y)
                        point2 = (x - (count + 1), y + 1)

                count = count + 1
                last_gem = game_state.gems[x][y]

                if controller_base.check_valid_turn(point1, point2):
                    return point1, point2
                elif point1 != (0, 0) and point2 != (0, 0):
                    logging.debug('invalid turn selected: x={},y={} {} -> {}'.format(x, y, point1, point2))

                point1 = point2 = (0, 0)

            # reset gem on next line
            last_gem = GemType.UNKNOWN
            count = 0

        return None, None
