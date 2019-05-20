import unittest

from card_utils.games.poker.omaha.brute_force import get_best_hand_brute_force, brute_force_omaha_hi_rank
from card_utils.games.poker.omaha.utils import get_best_hand, get_hand_strength
from card_utils.games.poker.util import pretty_hand_rank
from tests.games.poker.util import deal_random_board_hands


class BestOmahaHighHandTestCase(unittest.TestCase):
    """ Test for the best Omaha high hand """

    n_random_cases = 100

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_random_cases(self):
        for _ in range(self.n_random_cases):
            board, hands = deal_random_board_hands(n_hands=8, n_cards=4)
            self._test_best_hand(board, hands)

    def _test_best_hand(self, board, hands):
        """
        :param board: ([str])
        :param hands: ([{str}]) list of set of cards
        """
        true_best_hand_index = get_best_hand_brute_force(board, hands)
        test_best_hand_index = get_best_hand(board, hands)

        true_hand_rank = brute_force_omaha_hi_rank(board, hands[true_best_hand_index])
        calc_hand_rank = get_hand_strength(board, hands[test_best_hand_index])

        true_pretty_rank = pretty_hand_rank(true_hand_rank)
        calc_pretty_rank = pretty_hand_rank(calc_hand_rank)

        self.assertEqual(
            first=true_best_hand_index,
            second=test_best_hand_index,
            msg=(
                f'Board: {board}\n'
                f'Best hand is {hands[true_best_hand_index]} ({true_pretty_rank})\n'
                f'Test value: {hands[test_best_hand_index]} ({calc_pretty_rank})'
            )
        )
