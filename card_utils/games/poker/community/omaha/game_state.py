""" class for generic omaha game state """
from typing import List, Dict

from card_utils.games.poker.community.game_state import CommunityGameState
from card_utils.games.poker.community.omaha.utils import get_best_hands_fast


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
                 ante: int = 0,
                 blinds: List[int] = None,
                 street_actions: List[Dict] = None,
                 ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param starting_stacks: ([[int]])
        :param boards: ([[str]])
        :param blinds: ([int])
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
            ante=ante,
            blinds=blinds,
            street_actions=street_actions,
        )

    def order_hands(self, players):
        """
        :param players: ([int])
        :return: ([[int]])
        """
        # list of list of best hands,
        # outer list is a rank,
        # inner list is set of people who chop
        best_hands = get_best_hands_fast(
            board=self.board,
            hands=[self.hands[p] for p in players]
        )
        return [p for p, r in zip(players, best_hands)]
