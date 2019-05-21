""" class for generic omaha game state """
from typing import List

from card_utils.games.poker.community.game_state import CommunityGameState


class OmahaGameState(CommunityGameState):
    """ basic omaha game state """

    name = 'omaha'
    num_hole_cards = 4

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 stacks: List[int],
                 boards: List[List[str]] = None,
                 pot: int = 0,
                 small_blind: int = 1,
                 big_blind: int = 2):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param stacks: ([[int]])
        :param boards: ([[str]])
        :param pot: (int)
        :param small_blind: (int)
        :param big_blind: (int)
        """
        super().__init__(
            num_players=num_players,
            deck=deck,
            hands=hands,
            stacks=stacks,
            boards=boards,
            pot=pot,
            small_blind=small_blind,
            big_blind=big_blind
        )
