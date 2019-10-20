import controller_base
from model import *


class NaiveGameController(controller_base.AbstractGameController):
    """naive controller class that computes the next game turn based on pre programmed rules"""

    def next_turn(self, game_state: GameState) -> ((int, int), (int, int)):
        point1 = point2 = (0, 0)
        last_gem = GemType.UNKNOWN
        count = 0

        # TODO implement scan for vertical match

        # scan if we can get a horizontal match
        for y in reversed(range(COUNT_GEMS_V)):
            for x in range(COUNT_GEMS_H):
                if x == 7 and y == 3:
                    x = x
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

                count = count + 1
                last_gem = game_state.gems[x][y]

                if controller_base.check_valid_turn(point1, point2):
                    return point1, point2

            # reset gem on next line
            last_gem = GemType.UNKNOWN
            count = 0

        return None, None
