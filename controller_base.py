import abc
import model


class AbstractStateController(abc.ABC):
    @abc.abstractmethod
    def can_handle_game_state(self, game_state: model.GameState) -> bool:
        """to be implemented by derived classes to indicate if a given game state can be handled by this controller"""
        pass


class AbstractGameController(AbstractStateController):
    """abstract base class for a controller that handle the game phase GamePhase.IN_GAME"""

    def can_handle_game_state(self, game_state: model.GameState) -> bool:
        return game_state is not None and game_state.phase == model.GamePhase.IN_GAME

    @abc.abstractmethod
    def next_turn(self, game_state: model.GameState) -> ((int, int), (int, int)):
        """
        to be implemented by derived classes to compute the next turn that should take place
        return values should be 2 tuples from (0, 0) to (model.COUNT_GEMS_H, model.COUNT_GEMS_V) or None, None
        """
        pass


def check_valid_turn(point1: tuple, point2: tuple) -> bool:
    """checks if a given turn is valid"""
    if not model.check_bounds(point1) or not model.check_bounds(point2):
        return False
    return (point1[0] == point2[0] and (point1[1] == point2[1] + 1 or point1[1] == point2[1] - 1)) or \
           (point1[1] == point2[1] and (point1[0] == point2[0] + 1 or point1[0] == point2[0] - 1))
