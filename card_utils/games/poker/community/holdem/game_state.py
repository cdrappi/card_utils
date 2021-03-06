""" class for generic holdem game state """

from card_utils.games.poker.community.game_state import CommunityGameState
from card_utils.games.poker.community.holdem.utils import get_best_hands_fast


class HoldemGameState(CommunityGameState):
    """ basic holdem game state """

    name = "abstract_holdem"
    num_hole_cards = 2

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
            [players_at_showdown[i] for i in hand_level] for hand_level in best_hands
        ]
