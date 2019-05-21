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
                 big_blind: int = 2,
                 action: int = None,
                 street: int = 1):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param stacks: ([[int]])
        :param boards: ([[str]])
        :param pot: (int)
        :param small_blind: (int)
        :param big_blind: (int)
        :param action: (int) the player index who acts (0-indexed)
            --> if None, default is set based on number of players
        :param street: (int) the current street (1-indexed)
        """
        super().__init__(
            num_players=num_players,
            deck=deck,
            hands=hands,
            stacks=stacks,
            boards=boards,
            pot=pot,
            small_blind=small_blind,
            big_blind=big_blind,
            action=action,
            street=street
        )
