""" class for generic omaha game state """

from card_utils.games.poker.community.game_state import CommunityGameState
from card_utils.games.poker.community.omaha.utils import get_best_hands_fast


class OmahaGameState(CommunityGameState):
    """ basic omaha game state """

    name = 'abstract_omaha'
    num_hole_cards = 4

    def order_hands(self, players_at_showdown):
        """
        :param players_at_showdown: ([int])
        :return: ([[int]])
        """
        best_hands = get_best_hands_fast(
            board=self.board,
            hands=[self.hands[p] for p in players_at_showdown]
        )
        return [
            [players_at_showdown[i] for i in hand_level]
            for hand_level in best_hands
        ]
