""" class for generic omaha game state """
from typing import List

from card_utils.games.poker.community.game_state import CommunityGameState
from card_utils.games.poker.street_action import StreetAction


class OmahaGameState(CommunityGameState):
    """ basic omaha game state """

    name = 'abstract_omaha'
    num_hole_cards = 4

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 starting_stacks: List[int],
                 boards: List[List[str]] = None,
                 small_blind: int = 1,
                 big_blind: int = 2,
                 street_actions: List[List[StreetAction]] = None,
                 ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param starting_stacks: ([[int]])
        :param boards: ([[str]])
        :param small_blind: (int)
        :param big_blind: (int)
        :param street_actions: ([[int]])
            Each street gets a list of list of actions,
            represented by an object StreetAction
        """
        super().__init__(
            num_players=num_players,
            deck=deck,
            hands=hands,
            starting_stacks=starting_stacks,
            boards=boards,
            small_blind=small_blind,
            big_blind=big_blind,
            street_actions=street_actions,
        )
