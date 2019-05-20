import unittest

from card_utils.games.poker.omaha.brute_force import get_best_hand_brute_force
from card_utils.games.poker.omaha.utils import get_best_hand
from tests.games.poker.util import deal_random_board_hands


class TestBestOmahaHighHand(unittest.TestCase):
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
        calculated_best_hand_index = get_best_hand(board, hands)
        self.assertEqual(
            first=true_best_hand_index,
            second=calculated_best_hand_index,
            msg=(
                f'Board: {board}\n'
                f'Best hand is {hands[true_best_hand_index]}\n'
                f'Calculated: {hands[calculated_best_hand_index]}'
            )
        )
