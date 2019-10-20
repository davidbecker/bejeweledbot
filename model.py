from enum import Enum, IntEnum
from typing import List
import logging

# global level increase for now
logging.getLogger().setLevel(logging.DEBUG)


class GamePhase(Enum):
    UNKNOWN = 0,
    IN_MENU = 1,
    IN_GAME = 2,
    PAUSED = 3


class GemType(IntEnum):
    UNKNOWN = 0,
    YELLOW = 1,
    WHITE = 2,
    BLUE = 3,
    RED = 4,
    PURPLE = 5,
    ORANGE = 6,
    GREEN = 7


# number of gem types
NUM_GEMS = GemType.GREEN.value
# dimensions of the game board in gems
COUNT_GEMS_H = COUNT_GEMS_V = 8


class GameState:
    """class representing the current game state"""

    # unused at the moment
    phase: GamePhase

    # lists that represent the playing field ([0][0] is the lower left corner)
    gems: List[List[GemType]]
    certainty: List[List[float]]

    def reset(self) -> None:
        self.phase = GamePhase.UNKNOWN
        self.gems: List[List[GemType]] = [[GemType.UNKNOWN for j in range(COUNT_GEMS_H)] for i in range(COUNT_GEMS_V)]
        self.certainty: List[List[float]] = [[0.0 for j in range(COUNT_GEMS_H)] for i in range(COUNT_GEMS_V)]

    def __init__(self):
        self.reset()

    def get_gems_str(self) -> str:
        """gets a nicely formatted string representation of self.gems"""
        gems_list = ['+']
        for x in range(COUNT_GEMS_H - 1):
            gems_list.append('--')
        gems_list.append('-+\n')
        for y in reversed(range(COUNT_GEMS_V)):
            for x in range(COUNT_GEMS_H):
                if x == 0:
                    gems_list.append('|')
                gems_list.append('{}'.format(self.gems[x][y].value))
                if x == COUNT_GEMS_H - 1:
                    gems_list.append('|')
                else:
                    gems_list.append(' ')
            gems_list.append('\n')
        gems_list.append('+')
        for x in range(COUNT_GEMS_H - 1):
            gems_list.append('--')
        gems_list.append('-+\n')
        return ''.join(gems_list)

    def __str__(self):
        # ignore self.certainty for now
        return 'phase: {}\ngems:\n{}'.format(self.phase, self.get_gems_str())

    def __repr__(self):
        return 'phase={}, gems={}, certainty={}'.format(self.phase, self.gems, self.certainty)

    def add_gem(self, x: int, y: int, gem: GemType, certainty: float = 0.0) -> bool:
        """
        adds a gem with at a given point.

        Returns False on failed bound checks or at an attempt to override a gem with a lower certainty
        """
        if x is None or y is None:
            return False
        if x < 0 or x >= COUNT_GEMS_H or y < 0 or y >= COUNT_GEMS_V:
            logging.error('tried to add gem {} out of bounds at ({},{})'.format(gem.name, x, y))
            return False
        if self.certainty[x][y] > certainty:
            logging.error('tried to override gem {} (certainty {}) at ({},{}) with gem {} (certainty {})'.format(
                self.gems[x][y].name, self.certainty[x][y], x, y, gem.name, certainty))
            return False
        if self.gems[x][y] != GemType.UNKNOWN and self.gems[x][y] != gem:
            logging.debug('overridden gem {} (certainty {}) at ({},{}) with gem {} (certainty {})'.format(
                self.gems[x][y].name, self.certainty[x][y], x, y, gem.name, certainty))
        self.gems[x][y] = gem
        self.certainty[x][y] = certainty
        return True

    def check_board_complete(self) -> bool:
        for y in range(COUNT_GEMS_V):
            for x in range(COUNT_GEMS_H):
                if self.gems[x][y] == GemType.UNKNOWN:
                    return False
        return True


def check_bounds(point: tuple) -> bool:
    """checks if a given point matches the boundaries of the game board"""
    if point is None or not hasattr(point, '__len__') or point.__len__() < 2:
        raise ValueError('invalid point {} - expected tuple'.format(point))
    return 0 <= point[0] < COUNT_GEMS_H and 0 <= point[1] < COUNT_GEMS_V


def debug_get_neighbours(game_state: GameState, point: tuple) -> str:
    """helper function to get the surrounding gems of a position"""
    if game_state is None or not check_bounds(point):
        return ValueError()
    temp_list = []
    for dy in reversed(range(-1, 2)):
        for dx in range(-1, 2):
            if check_bounds((point[0]+dx, point[1]+dy)):
                temp_list.append('{}'.format(game_state.gems[point[0]+dx][point[1]+dy].value))
            else:
                temp_list.append('#')
        temp_list.append('\n')
    return ''.join(temp_list)


