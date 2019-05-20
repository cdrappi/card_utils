import unittest

from card_utils.games.poker.omaha.brute_force import get_best_hand_brute_force
from card_utils.games.poker.omaha.utils import get_best_hand


class BestOmahaHighHand(unittest.TestCase):
    """ Test for the best Omaha high hand """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _test_best_hand(self, board, hands):
        """
        :param board: ([str])
        :param hands: ([{str}]) list of set of cards
        """
        true_best_hand_index = get_best_hand_brute_force(board, hands)
        calculated_best_hand_index = get_best_hand(board, hands)
        self.assertEqual(true_best_hand_index, calculated_best_hand_index)
